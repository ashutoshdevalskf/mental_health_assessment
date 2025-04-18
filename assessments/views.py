import json
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from .forms import AssessmentForm
from .models import AssessmentAttempt
from .utils import calculate_disorder_scores
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import os
from .models import Assessment, AssessmentAttempt
from collections import defaultdict
import io
import base64
import matplotlib.pyplot as plt

ASSESSMENT_JSON = {
    1: 'questionnaire.json',   # General Mental Health Test
    2: 'phq9.json',            # Depression‑specific
    3: 'gad7.json',            # Anxiety‑specific
    4: 'oci-r.json',           # OCD‑specific
}

class QuestionMock:
    def __init__(self, data):
        self.id = data['id']
        self.text = data['text']
        self.reverse_scored = data.get('reverse_scored', False)
        self.weight = data.get('weight', 1)
        self.disorders = data['disorders']

@login_required
def select_assessment_view(request):
    assessments = Assessment.objects.all()
    return render(request, 'assessment_select.html', {'assessments': assessments})

@login_required
def assessment_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    filename = ASSESSMENT_JSON.get(assessment_id)
    questions_path = os.path.join(settings.BASE_DIR, 'resources', filename)

    with open(questions_path, 'r') as f:
        questions_data = json.load(f)

    question_objs = [QuestionMock(q) for q in questions_data]
    total_questions = len(question_objs)

    key_curr = f'current_q_{assessment_id}'
    key_resp = f'responses_{assessment_id}'
    current_q = request.session.get(key_curr, 0)
    responses = request.session.get(key_resp, {})

    if request.method == 'POST':
        answer = request.POST['answer']
        qid = f'question-{question_objs[current_q].id}'
        responses[qid] = answer
        request.session[key_resp] = responses

        current_q += 1
        if current_q >= total_questions:
            question_bank = {
                q.id: {
                    "disorders": q.disorders,
                    "reverse_scored": q.reverse_scored,
                    "weight": q.weight
                }
                for q in question_objs
            }

            formatted_responses = [
                {"question_id": q.id, "answer": responses[f"question-{q.id}"]}
                for q in question_objs
            ]

            raw_scores, severity_scores = calculate_disorder_scores(
                formatted_responses,
                question_bank
            )

            AssessmentAttempt.objects.create(
                user=request.user,
                assessment=assessment,
                score=sum(int(r["answer"]) for r in formatted_responses),
                responses=formatted_responses,
                raw_scores=raw_scores,
                severity_scores=severity_scores
            )

            request.session['latest_results'] = {
                'severity': severity_scores,
                'raw': raw_scores
            }

            request.session.pop(key_curr, None)
            request.session.pop(key_resp, None)

            return redirect('results')

        request.session[key_curr] = current_q
        return redirect('assessment', assessment_id=assessment_id)

    question = question_objs[current_q]
    return render(request, 'question_page.html', {
        'assessment_title': assessment.title,
        'question': question,
        'question_number': current_q + 1,
        'total': total_questions,
    })

@login_required
def results_view(request):
    latest_results = request.session.get('latest_results', {})
    severity_scores = latest_results.get('severity', {})
    raw_scores = latest_results.get('raw', {})

    severity_to_percent = {
        'none': 0,
        'mild': 25,
        'moderate': 50,
        'moderately severe': 75,
        'severe': 100
    }

    severity_to_color = {
        'none': '#4CAF50',
        'mild': '#FFC107',
        'moderate': '#FF9800',
        'moderately severe': '#FF5722',
        'severe': '#F44336'
    }

    results_with_visual = []
    for disorder, severity in severity_scores.items():
        severity_key = severity.lower()
        percent = severity_to_percent.get(severity_key, 0)
        dash_array = 314
        dash_offset = dash_array - int((dash_array * percent) / 100)
        color = severity_to_color.get(severity_key, '#4CAF50')
        raw_score = raw_scores.get(disorder, 0)

        results_with_visual.append({
            'disorder': disorder,
            'severity': severity,
            'percent': percent,
            'raw_score': raw_score,
            'dash_offset': dash_offset,
            'color': color
        })

    return render(request, 'results.html', {'results': results_with_visual})



@login_required
def profile_view(request):
    attempts = AssessmentAttempt.objects.filter(user=request.user).order_by('-attempted_at')

    return render(request, 'profile.html', {'attempts': attempts})

from .forms import CustomUserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('profile')  # or wherever you want to redirect after login
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')  # Your custom login template

@login_required
def statistic_view(request):
    user = request.user
    attempts = user.assessmentattempt_set.order_by('attempted_at')

    labels = [attempt.attempted_at.strftime("%b %d") for attempt in attempts]

    SEVERITY_MAP = {
        'none': 0,
        'mild': 1,
        'moderate': 2,
        'moderately severe': 3,
        'severe': 4
    }

    disorder_scores = {}
    for attempt in attempts:
        for disorder, severity in attempt.severity_scores.items():
            disorder = disorder.lower()
            severity_value = SEVERITY_MAP.get(severity.lower(), None)
            if severity_value is not None:
                disorder_scores.setdefault(disorder, []).append(severity_value)

    context = {
        'labels': labels,
        'disorder_scores': disorder_scores,
    }
    return render(request, 'statistics.html', context)


def about_view(request):
    return render(request, 'about.html')

def get_help_view(request):
    return render(request, 'get_help.html')

