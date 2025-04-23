from django.urls import path
from . import views

urlpatterns = [
    path('assessment/', views.select_assessment_view, name='select_assessment'),

    
    path('assessment/<int:assessment_id>/', 
         views.assessment_view, 
         name='assessment'),
    path('results/', views.results_view, name='results'),
    path('profile/', views.profile_view, name='profile'),
    path('statistics/', views.statistic_view, name='statistics'),
    path('history/', views.history_view, name='history'),
    path('history/delete/<int:attempt_id>/', views.history_delete_view, name='history_delete'),
]