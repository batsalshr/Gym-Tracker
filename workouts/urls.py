"""URL patterns for workouts app."""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Workout flow
    path('workout/new/', views.NewWorkoutView.as_view(), name='new_workout'),
    path('workout/<int:workout_id>/add-exercise/', views.AddExerciseView.as_view(), name='add_exercise'),
    path('workout/<int:workout_id>/exercise/<int:exercise_id>/sets/', views.EnterSetsView.as_view(), name='enter_sets'),
    path('workout/<int:workout_id>/', views.WorkoutDetailView.as_view(), name='workout_detail'),
    path('workout/<int:workout_id>/delete/', views.DeleteWorkoutView.as_view(), name='delete_workout'),
    
    # Workouts list
    path('workouts/', views.WorkoutListView.as_view(), name='workout_list'),
    
    # Exercises
    path('exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('exercises/add/', views.AddExerciseTypeView.as_view(), name='add_exercise_type'),
    
    # Personal Bests
    path('personal-bests/', views.PersonalBestsView.as_view(), name='personal_bests'),
    
    # API
    path('api/exercise/<int:exercise_id>/suggestion/', views.ExerciseSuggestionAPI.as_view(), name='api_suggestion'),
]
