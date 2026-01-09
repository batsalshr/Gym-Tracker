"""URL patterns for workouts app."""
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
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
    path('exercises/<int:exercise_id>/delete/', views.DeleteExerciseView.as_view(), name='delete_exercise'),
    path('exercises/<int:exercise_id>/progress/', views.ProgressView.as_view(), name='exercise_progress'),
    
    # Sets
    path('set/<int:set_id>/delete/', views.DeleteSetView.as_view(), name='delete_set'),
    
    # Body Weight
    path('bodyweight/', views.BodyWeightView.as_view(), name='bodyweight'),
    path('bodyweight/<int:weight_id>/delete/', views.DeleteBodyWeightView.as_view(), name='delete_bodyweight'),
    
    # Body Measurements
    path('measurements/', views.MeasurementsView.as_view(), name='measurements'),
    path('measurements/<int:measurement_id>/delete/', views.DeleteMeasurementView.as_view(), name='delete_measurement'),
    
    # Templates
    path('templates/', views.TemplatesView.as_view(), name='templates'),
    path('templates/<int:template_id>/edit/', views.TemplateEditView.as_view(), name='template_edit'),
    path('templates/<int:template_id>/delete/', views.DeleteTemplateView.as_view(), name='delete_template'),
    path('templates/<int:template_id>/use/', views.UseTemplateView.as_view(), name='use_template'),
    path('templates/exercise/<int:exercise_id>/delete/', views.DeleteTemplateExerciseView.as_view(), name='delete_template_exercise'),
    
    # Goals
    path('goals/', views.GoalsView.as_view(), name='goals'),
    path('goals/<int:goal_id>/update/', views.UpdateGoalView.as_view(), name='update_goal'),
    path('goals/<int:goal_id>/delete/', views.DeleteGoalView.as_view(), name='delete_goal'),
    
    # New Features
    path('calculator/', views.CalculatorView.as_view(), name='calculator'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('charts/', views.ChartsView.as_view(), name='charts'),
    path('achievements/', views.AchievementsView.as_view(), name='achievements'),
    
    # API
    path('api/exercise/<int:exercise_id>/suggestion/', views.ExerciseSuggestionAPI.as_view(), name='api_suggestion'),
    path('api/exercises/search/', views.ExerciseSearchAPI.as_view(), name='api_exercise_search'),
]
