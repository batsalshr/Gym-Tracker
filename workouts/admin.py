"""
Django admin configuration for gym workout tracking.
"""

from django.contrib import admin
from .models import Exercise, WorkoutSession, Set


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_group', 'created_at']
    search_fields = ['name', 'muscle_group']
    list_filter = ['muscle_group']


class SetInline(admin.TabularInline):
    model = Set
    extra = 3
    fields = ['exercise', 'weight', 'reps', 'notes']


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['date', 'duration_minutes', 'get_set_count', 'created_at']
    list_filter = ['date']
    search_fields = ['notes']
    inlines = [SetInline]
    date_hierarchy = 'date'

    def get_set_count(self, obj):
        return obj.sets.count()
    get_set_count.short_description = 'Sets'


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ['session', 'exercise', 'weight', 'reps', 'notes']
    list_filter = ['exercise', 'session__date']
    search_fields = ['exercise__name', 'notes']
    raw_id_fields = ['session']
