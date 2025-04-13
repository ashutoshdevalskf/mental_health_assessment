import json
from django.conf import settings
from django.shortcuts import render, redirect
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

@login_required
def assessment_view(request):
    questions_path = os.path.join(settings.BASE_DIR, 'resources', 'questionnaire.json')
    with open(questions_path, 'r') as f:
        questions_data = json.load(f)

    class QuestionMock:
        def __init__(self, data):
            self.id = data['id']
            self.text = data['text']
            self.reverse_scored = data.get('reverse_scored', False)
            self.weight = data.get('weight', 1)
            self.disorders = data['disorders']

    question_objs = [QuestionMock(q) for q in questions_data]
    total_questions = len(question_objs)

    current_q = request.session.get('current_q', 0)
    responses = request.session.get('responses', {})

    if request.method == 'POST':
        answer = request.POST.get('answer')
        qid = f'question-{question_objs[current_q].id}'
        responses[qid] = answer
        request.session['responses'] = responses

        current_q += 1
        if current_q >= total_questions:
            # All questions answered
            question_bank = {
                q.id: {"disorders": q.disorders, "reverse_scored": q.reverse_scored, "weight": q.weight}
                for q in question_objs
            }
            formatted_responses = [
                {"question_id": q.id, "answer": responses[f'question-{q.id}']}
                for q in question_objs
            ]

            raw_scores, severity_scores = calculate_disorder_scores(formatted_responses, question_bank)
            assessment = Assessment.objects.get(title="General Mental Health Test")

            AssessmentAttempt.objects.create(
                user=request.user,
                assessment=assessment,
                score=sum(int(r["answer"]) for r in formatted_responses),
                responses=formatted_responses,
                raw_scores=raw_scores,
                severity_scores=severity_scores
            )

            # Clear session
            request.session.pop('current_q', None)
            request.session.pop('responses', None)
            request.session['latest_results'] = severity_scores

            return redirect('results')

        request.session['current_q'] = current_q
        return redirect('assessment')

    # Show current question
    question = question_objs[current_q]
    return render(request, 'question_page.html', {'question': question, 'question_number': current_q + 1, 'total': total_questions})


@login_required
def results_view(request):
    latest_results = request.session.get('latest_results')

    severity_to_percent = {
        'none': 0,
        'mild': 25,
        'moderate': 50,
        'moderately severe': 75,
        'severe': 100
    }

    severity_to_color = {
        'none': '#4CAF50',         # Green
        'mild': '#FFC107',         # Amber
        'moderate': '#FF9800',     # Orange
        'moderately severe': '#FF5722', # Deep Orange
        'severe': '#F44336'        # Red
    }

    results_with_visual = []
    for disorder, severity in latest_results.items():
        severity_key = severity.lower()
        percent = severity_to_percent.get(severity_key, 0)
        dash_array = 314
        dash_offset = dash_array - int((dash_array * percent) / 100)
        color = severity_to_color.get(severity_key, '#4CAF50')
        results_with_visual.append({
            'disorder': disorder,
            'severity': severity,
            'percent': percent,
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
def statistics_view(request):
    user = request.user
    attempts = AssessmentAttempt.objects.filter(user=user)

    num_attempts = attempts.count()
    average_score = round(sum(a.score for a in attempts) / num_attempts, 2) if num_attempts else 0
    latest_attempt = attempts.order_by('-attempted_at').first()

    disorder_scores = defaultdict(list)
    for attempt in attempts:
        for disorder, score in attempt.severity_scores.items():
            try:
                disorder_scores[disorder].append(float(score))
            except ValueError:
                pass

    average_severity = {
        disorder: round(sum(scores) / len(scores), 2)
        for disorder, scores in disorder_scores.items() if scores
    }

    # Prepare data for Chart.js
    chart_labels = json.dumps(list(average_severity.keys()))
    chart_data = json.dumps(list(average_severity.values()))

    context = {
        'num_attempts': num_attempts,
        'average_score': average_score,
        'latest_attempt': latest_attempt,
        'average_severity': average_severity,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'statistics.html', context)