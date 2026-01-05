"""
App configuration for workouts.
"""

from django.apps import AppConfig


class WorkoutsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workouts'
    verbose_name = 'Gym Workout Tracker'
