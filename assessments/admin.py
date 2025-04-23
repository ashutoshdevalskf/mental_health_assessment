from django.contrib import admin
from .models import Question, Assessment, AssessmentAttempt

# Register the models in the admin panel
admin.site.register(Question)
admin.site.register(Assessment)
admin.site.register(AssessmentAttempt)