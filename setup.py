#!/usr/bin/env python
"""
Setup script for Gym Tracker.
Initializes the database and optionally adds sample exercises.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_tracker.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from workouts.models import Exercise

# Sample exercises to populate the database
SAMPLE_EXERCISES = [
    {'name': 'Bench Press', 'muscle_group': 'Chest', 'description': 'Barbell bench press - primary chest exercise'},
    {'name': 'Incline Bench Press', 'muscle_group': 'Chest', 'description': 'Upper chest focus'},
    {'name': 'Deadlift', 'muscle_group': 'Back', 'description': 'Conventional deadlift'},
    {'name': 'Squat', 'muscle_group': 'Legs', 'description': 'Back squat - the king of leg exercises'},
    {'name': 'Overhead Press', 'muscle_group': 'Shoulders', 'description': 'Standing barbell overhead press'},
    {'name': 'Barbell Row', 'muscle_group': 'Back', 'description': 'Bent-over barbell row'},
    {'name': 'Pull-up', 'muscle_group': 'Back', 'description': 'Bodyweight pull-up'},
    {'name': 'Dumbbell Curl', 'muscle_group': 'Arms', 'description': 'Standing dumbbell bicep curl'},
    {'name': 'Tricep Pushdown', 'muscle_group': 'Arms', 'description': 'Cable tricep pushdown'},
    {'name': 'Leg Press', 'muscle_group': 'Legs', 'description': 'Machine leg press'},
    {'name': 'Lat Pulldown', 'muscle_group': 'Back', 'description': 'Cable lat pulldown'},
    {'name': 'Leg Curl', 'muscle_group': 'Legs', 'description': 'Seated or lying leg curl'},
    {'name': 'Leg Extension', 'muscle_group': 'Legs', 'description': 'Machine leg extension'},
    {'name': 'Dumbbell Shoulder Press', 'muscle_group': 'Shoulders', 'description': 'Seated dumbbell press'},
    {'name': 'Lateral Raise', 'muscle_group': 'Shoulders', 'description': 'Dumbbell lateral raise'},
    {'name': 'Face Pull', 'muscle_group': 'Shoulders', 'description': 'Cable face pull for rear delts'},
    {'name': 'Romanian Deadlift', 'muscle_group': 'Legs', 'description': 'RDL for hamstrings'},
    {'name': 'Dip', 'muscle_group': 'Chest', 'description': 'Parallel bar dip'},
    {'name': 'Cable Fly', 'muscle_group': 'Chest', 'description': 'Cable chest fly'},
    {'name': 'Plank', 'muscle_group': 'Core', 'description': 'Front plank hold'},
]


def setup_database():
    """Run migrations to create database tables."""
    print("Running migrations...")
    call_command('migrate', verbosity=1)
    print("✓ Database setup complete!")


def create_sample_exercises():
    """Create sample exercises if they don't exist."""
    print("\nAdding sample exercises...")
    created_count = 0
    
    for exercise_data in SAMPLE_EXERCISES:
        exercise, created = Exercise.objects.get_or_create(
            name=exercise_data['name'],
            defaults={
                'muscle_group': exercise_data['muscle_group'],
                'description': exercise_data['description']
            }
        )
        if created:
            created_count += 1
            print(f"  + Created: {exercise.name}")
    
    print(f"✓ Added {created_count} new exercises ({Exercise.objects.count()} total)")


def main():
    print("=" * 50)
    print("Gym Tracker Setup")
    print("=" * 50)
    
    # Setup database
    setup_database()
    
    # Ask about sample data
    if '--no-sample' not in sys.argv:
        response = input("\nWould you like to add sample exercises? [Y/n]: ").strip().lower()
        if response in ('', 'y', 'yes'):
            create_sample_exercises()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nTo start the server, run:")
    print("  python manage.py runserver")
    print("\nThen open http://localhost:8000 in your browser.")
    print("=" * 50)


if __name__ == '__main__':
    main()
