from django.contrib import admin
from .models import Exercise, Workout, Set, BodyWeight, WorkoutTemplate, TemplateExercise, Goal

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_group', 'equipment']
    list_filter = ['muscle_group', 'equipment']
    search_fields = ['name']

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['date', 'muscle_groups', 'get_total_sets']
    list_filter = ['date']
    search_fields = ['muscle_groups', 'notes']

@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ['workout', 'exercise', 'weight', 'reps', 'set_number']
    list_filter = ['exercise__muscle_group', 'exercise']
    search_fields = ['exercise__name']

@admin.register(BodyWeight)
class BodyWeightAdmin(admin.ModelAdmin):
    list_display = ['date', 'weight', 'notes']
    list_filter = ['date']

@admin.register(WorkoutTemplate)
class WorkoutTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_groups']

@admin.register(TemplateExercise)
class TemplateExerciseAdmin(admin.ModelAdmin):
    list_display = ['template', 'exercise', 'target_sets', 'target_reps']

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'goal_type', 'target_value', 'current_value', 'status']
    list_filter = ['goal_type', 'status']
