from django.urls import path
from . import views

urlpatterns = [
    path('assessment/', views.assessment_view, name='assessment'),
    path('results/', views.results_view, name='results'),
    path('profile/', views.profile_view, name='profile'),
    path('statistics/', views.statistics_view, name='statistics'),
]