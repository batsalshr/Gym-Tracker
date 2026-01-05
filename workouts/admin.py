from django.contrib import admin
from .models import Exercise, Workout, Set

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_group']
    list_filter = ['muscle_group']

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['date', 'day_type', 'get_total_sets']
    list_filter = ['day_type', 'date']

@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ['workout', 'exercise', 'weight', 'reps']
    list_filter = ['exercise']
