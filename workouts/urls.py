"""
URL patterns for gym workout tracking.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Sessions
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/new/', views.SessionCreateView.as_view(), name='session_create'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),
    path('sessions/<int:session_id>/add-set/', views.AddSetToSessionView.as_view(), name='add_set'),
    
    # Sets
    path('sets/<int:set_id>/delete/', views.DeleteSetView.as_view(), name='delete_set'),
    
    # Exercises
    path('exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('exercises/new/', views.ExerciseCreateView.as_view(), name='exercise_create'),
    path('exercises/<int:pk>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('exercises/<int:pk>/delete/', views.ExerciseDeleteView.as_view(), name='exercise_delete'),
    
    # Personal Bests
    path('personal-bests/', views.PersonalBestsView.as_view(), name='personal_bests'),
    
    # API endpoints
    path('api/exercises/search/', views.ExerciseSuggestionsAPI.as_view(), name='api_exercise_search'),
    path('api/exercises/<int:exercise_id>/progression/', views.ExerciseProgressionAPI.as_view(), name='api_exercise_progression'),
]
