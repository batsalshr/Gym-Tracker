"""URL patterns for workouts app."""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Log workout flow
    path('log/', views.LogWorkoutView.as_view(), name='log_workout'),
    path('log/<int:workout_id>/exercises/', views.AddExercisesView.as_view(), name='add_exercises'),
    
    # Workout views
    path('workout/<int:workout_id>/', views.WorkoutDetailView.as_view(), name='workout_detail'),
    path('workout/<int:workout_id>/delete/', views.DeleteWorkoutView.as_view(), name='delete_workout'),
    
    # History
    path('history/', views.HistoryView.as_view(), name='history'),
    
    # Personal Bests
    path('personal-bests/', views.PersonalBestsView.as_view(), name='personal_bests'),
    
    # Exercises
    path('exercises/', views.ExerciseListView.as_view(), name='exercises'),
    
    # Sets
    path('set/<int:set_id>/delete/', views.DeleteSetView.as_view(), name='delete_set'),
    
    # API
    path('api/exercise/<int:exercise_id>/suggestion/', views.ExerciseSuggestionAPI.as_view(), name='api_suggestion'),
]
