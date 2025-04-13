from django import forms
from .models import Question

class AssessmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        SCALE = [(str(i), label) for i, label in enumerate([
            "Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"
        ])]
        for question in questions:
            self.fields[f'question-{question.id}'] = forms.ChoiceField(
                label=question.text,
                choices=SCALE,
                widget=forms.RadioSelect,
                required=True
            )

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')