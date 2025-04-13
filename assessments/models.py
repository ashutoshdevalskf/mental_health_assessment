from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Question(models.Model):
    text = models.TextField()
    disorders = models.JSONField()  # Example: ["depression", "anxiety"]
    reverse_scored = models.BooleanField(default=False)
    weight = models.IntegerField(default=1)

    def get_disorders_list(self):
        return self.disorders

    def __str__(self):
        return self.text
    


class Assessment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    def __str__(self):
        return self.title

class AssessmentAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.FloatField()
    attempted_at = models.DateTimeField(auto_now_add=True)
    responses = models.JSONField()
    raw_scores = models.JSONField()
    severity_scores = models.JSONField()


    def __str__(self):
        return f"{self.user.username} - {self.assessment.title} ({self.score})"


