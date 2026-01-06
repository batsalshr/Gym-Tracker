#!/usr/bin/env python
"""
Demo Data Generator for Gym Tracker

Creates realistic workout history with progressive overload.
Run after load_exercises.py

Usage:
    python demo_data.py
"""
import os
import sys
import random
from datetime import timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_tracker.settings')

import django
django.setup()

from django.utils import timezone
from workouts.models import (
    Exercise, Workout, Set, 
    BodyWeight, WorkoutTemplate, TemplateExercise, Goal
)


# Workout configurations
WORKOUT_TYPES = [
    {'name': 'Push Day', 'groups': ['chest', 'shoulders', 'triceps']},
    {'name': 'Pull Day', 'groups': ['back', 'biceps', 'forearms']},
    {'name': 'Leg Day', 'groups': ['legs', 'glutes', 'calves']},
    {'name': 'Upper Body', 'groups': ['chest', 'back', 'shoulders']},
    {'name': 'Chest & Triceps', 'groups': ['chest', 'triceps']},
    {'name': 'Back & Biceps', 'groups': ['back', 'biceps']},
]

# Base weights for common exercises (in kg)
BASE_WEIGHTS = {
    'Barbell Bench Press': 60,
    'Incline Dumbbell Bench Press': 22,
    'Dumbbell Fly': 14,
    'Deadlift': 100,
    'Barbell Row': 60,
    'Lat Pulldown': 50,
    'Back Squat': 80,
    'Leg Press': 120,
    'Leg Extension': 40,
    'Dumbbell Shoulder Press': 18,
    'Lateral Raise': 10,
    'Overhead Press': 40,
    'Barbell Curl': 30,
    'Dumbbell Curl': 12,
    'Hammer Curl': 14,
    'Tricep Pushdown': 25,
    'Skull Crusher': 25,
    'Cable Fly': 15,
    'Face Pull': 20,
    'Romanian Deadlift': 70,
    'Leg Curl': 35,
    'Calf Raise': 60,
}


def get_weight_for_exercise(exercise_name, workout_num):
    """Get progressive weight for an exercise."""
    base = BASE_WEIGHTS.get(exercise_name, 20)
    # Add ~1kg every 2 workouts for progression
    progression = Decimal(str(workout_num * 0.5))
    variance = Decimal(str(random.choice([-2.5, 0, 0, 2.5])))
    return max(Decimal('5'), Decimal(str(base)) + progression + variance)


def create_templates():
    """Create workout templates."""
    print("Creating workout templates...")
    
    templates_created = 0
    for wt in WORKOUT_TYPES:
        template, created = WorkoutTemplate.objects.get_or_create(
            name=wt['name'],
            defaults={'muscle_groups': ','.join(wt['groups'])}
        )
        
        if created:
            templates_created += 1
            # Add some exercises to each template
            exercises = Exercise.objects.filter(muscle_group__in=wt['groups'])[:5]
            for i, ex in enumerate(exercises):
                TemplateExercise.objects.create(
                    template=template,
                    exercise=ex,
                    order=i,
                    target_sets=random.choice([3, 4]),
                    target_reps=random.choice(['6-8', '8-10', '8-12', '10-12'])
                )
    
    print(f"  Created {templates_created} templates")


def create_workouts():
    """Create demo workout history."""
    print("Creating workout history...")
    
    today = timezone.now().date()
    workouts_created = 0
    
    # Create 15 workouts over the past 30 days
    for i in range(15):
        days_ago = random.randint(0, 30)
        workout_date = today - timedelta(days=days_ago)
        
        # Pick a random workout type
        wt = random.choice(WORKOUT_TYPES)
        
        workout = Workout.objects.create(
            date=workout_date,
            muscle_groups=','.join(wt['groups']),
            notes=random.choice(['', '', 'Great session!', 'Feeling strong', 'Quick workout'])
        )
        workouts_created += 1
        
        # Get exercises for this workout
        exercises = list(Exercise.objects.filter(
            muscle_group__in=wt['groups'],
            equipment__in=['barbell', 'dumbbell', 'machine', 'cable']
        ).exclude(name__icontains='plank').exclude(name__icontains='hold'))
        
        # Pick 4-6 exercises
        num_exercises = random.randint(4, 6)
        selected = random.sample(exercises, min(num_exercises, len(exercises)))
        
        for exercise in selected:
            # Create 3-4 sets per exercise
            num_sets = random.choice([3, 3, 4])
            base_weight = get_weight_for_exercise(exercise.name, i)
            
            for set_num in range(1, num_sets + 1):
                # Weight might drop slightly on later sets
                weight_drop = Decimal(str((set_num - 1) * random.choice([0, 0, 2.5])))
                weight = max(Decimal('5'), base_weight - weight_drop)
                
                # Reps typically decrease as sets go on
                base_reps = random.randint(8, 12)
                reps = max(5, base_reps - (set_num - 1))
                
                Set.objects.create(
                    workout=workout,
                    exercise=exercise,
                    set_number=set_num,
                    weight=weight,
                    reps=reps
                )
    
    print(f"  Created {workouts_created} workouts")


def create_bodyweights():
    """Create body weight entries."""
    print("Creating body weight entries...")
    
    today = timezone.now().date()
    base_weight = Decimal('75.0')
    
    entries_created = 0
    for i in range(14):  # 2 weeks of entries
        date = today - timedelta(days=i * 2)  # Every other day
        variance = Decimal(str(random.uniform(-0.5, 0.5)))
        trend = Decimal(str(i * -0.05))  # Slight downward trend
        
        weight = base_weight + variance + trend
        
        BodyWeight.objects.get_or_create(
            date=date,
            defaults={'weight': round(weight, 1)}
        )
        entries_created += 1
    
    print(f"  Created {entries_created} body weight entries")


def create_goals():
    """Create sample goals."""
    print("Creating goals...")
    
    goals_data = [
        {
            'name': 'Bench Press 100kg',
            'goal_type': 'weight',
            'exercise_name': 'Barbell Bench Press',
            'target_value': 100,
        },
        {
            'name': 'Squat 120kg',
            'goal_type': 'weight',
            'exercise_name': 'Back Squat',
            'target_value': 120,
        },
        {
            'name': 'Reach 73kg',
            'goal_type': 'bodyweight',
            'target_value': 73,
        },
    ]
    
    goals_created = 0
    for g in goals_data:
        exercise = None
        if 'exercise_name' in g:
            exercise = Exercise.objects.filter(name=g['exercise_name']).first()
        
        goal, created = Goal.objects.get_or_create(
            name=g['name'],
            defaults={
                'goal_type': g['goal_type'],
                'exercise': exercise,
                'target_value': g['target_value'],
                'deadline': timezone.now().date() + timedelta(days=90)
            }
        )
        
        if created:
            goal.update_progress()
            goals_created += 1
    
    print(f"  Created {goals_created} goals")


def main():
    print("\n🏋️ Gym Tracker Demo Data Generator\n")
    print("-" * 40)
    
    # Check if data exists
    if Workout.objects.exists():
        response = input("⚠️  Existing workouts found. Delete all data? (y/N): ")
        if response.lower() == 'y':
            print("\nClearing existing data...")
            Set.objects.all().delete()
            Workout.objects.all().delete()
            BodyWeight.objects.all().delete()
            Goal.objects.all().delete()
            TemplateExercise.objects.all().delete()
            WorkoutTemplate.objects.all().delete()
            print("  Done")
        else:
            print("Keeping existing data, adding more...")
    
    print()
    create_templates()
    create_workouts()
    create_bodyweights()
    create_goals()
    
    print()
    print("-" * 40)
    print("\n✅ Demo data created successfully!")
    print(f"\n   Workouts: {Workout.objects.count()}")
    print(f"   Sets: {Set.objects.count()}")
    print(f"   Templates: {WorkoutTemplate.objects.count()}")
    print(f"   Body Weight Entries: {BodyWeight.objects.count()}")
    print(f"   Goals: {Goal.objects.count()}")
    print()


if __name__ == '__main__':
    main()
