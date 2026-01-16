"""
Generate demo data for IronLog gym tracker.
Creates realistic workout history, body weight entries, measurements, and goals.
"""
import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_tracker.settings')
import django
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from workouts.models import (
    Exercise, Workout, Set, BodyWeight, 
    BodyMeasurement, Goal, WorkoutTemplate, 
    TemplateExercise, UserProfile
)


def create_demo_user():
    """Create or get demo user."""
    user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@ironlog.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        print(f"Created demo user: demo / demo123")
    else:
        print(f"Demo user already exists")
    
    # Ensure profile exists
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.display_name = "Demo User"
    profile.bio = "Fitness enthusiast on a strength journey!"
    profile.avatar_color = "#3b82f6"
    profile.save()
    
    return user


def get_exercises_by_muscle():
    """Get exercises grouped by muscle group."""
    exercises = {}
    for muscle, _ in Exercise.MUSCLE_GROUPS:
        exercises[muscle] = list(Exercise.objects.filter(muscle_group=muscle, user__isnull=True))
    return exercises


def generate_workouts(user, days=90):
    """Generate realistic workout history."""
    print(f"\nGenerating {days} days of workout history...")
    
    exercises_by_muscle = get_exercises_by_muscle()
    today = timezone.now().date()
    
    # Workout split patterns
    SPLITS = {
        'push': ['chest', 'shoulders', 'triceps'],
        'pull': ['back', 'biceps', 'forearms'],
        'legs': ['legs', 'glutes', 'calves'],
        'upper': ['chest', 'back', 'shoulders', 'biceps', 'triceps'],
        'lower': ['legs', 'glutes', 'calves'],
        'chest_back': ['chest', 'back'],
        'arms': ['biceps', 'triceps', 'forearms'],
        'shoulders': ['shoulders', 'traps'],
        'full_body': ['chest', 'back', 'legs', 'shoulders'],
    }
    
    # Weekly schedule (which days to workout)
    # 0=Monday, 6=Sunday
    workout_days = [0, 1, 2, 3, 4]  # Mon-Fri typically
    
    # Base weights for common exercises (will progress over time)
    BASE_WEIGHTS = {
        'Barbell Bench Press': 60,
        'Incline Dumbbell Bench Press': 22,
        'Dumbbell Fly': 14,
        'Cable Crossover': 15,
        'Push-Up': 0,
        'Deadlift': 80,
        'Barbell Row': 50,
        'Pull-Up': 0,
        'Lat Pulldown': 50,
        'Seated Cable Row': 45,
        'Back Squat': 70,
        'Leg Press': 120,
        'Leg Extension': 40,
        'Leg Curl': 35,
        'Romanian Deadlift': 50,
        'Overhead Press': 35,
        'Dumbbell Shoulder Press': 18,
        'Lateral Raise': 10,
        'Face Pull': 25,
        'Barbell Curl': 25,
        'Dumbbell Curl': 12,
        'Hammer Curl': 14,
        'Tricep Pushdown': 30,
        'Skullcrusher': 25,
        'Overhead Tricep Extension': 20,
        'Plank': 0,
        'Cable Crunch': 40,
        'Hanging Leg Raise': 0,
    }
    
    workouts_created = 0
    sets_created = 0
    
    for day_offset in range(days, 0, -1):
        workout_date = today - timedelta(days=day_offset)
        day_of_week = workout_date.weekday()
        
        # Skip some days randomly (rest days, missed workouts)
        if day_of_week not in workout_days:
            continue
        if random.random() < 0.15:  # 15% chance to skip
            continue
        
        # Choose a split based on day
        if day_of_week == 0:  # Monday - Push
            split = 'push'
        elif day_of_week == 1:  # Tuesday - Pull
            split = 'pull'
        elif day_of_week == 2:  # Wednesday - Legs
            split = 'legs'
        elif day_of_week == 3:  # Thursday - Upper
            split = 'upper'
        elif day_of_week == 4:  # Friday - Lower or Arms
            split = random.choice(['lower', 'arms'])
        else:
            split = random.choice(list(SPLITS.keys()))
        
        muscle_groups = SPLITS[split]
        
        # Create workout
        workout = Workout.objects.create(
            user=user,
            date=workout_date,
            muscle_groups=','.join(muscle_groups),
            duration_minutes=random.randint(45, 90),
            notes=f"{split.replace('_', ' ').title()} Day" if random.random() < 0.3 else ""
        )
        workouts_created += 1
        
        # Add exercises for each muscle group
        for muscle in muscle_groups:
            available = exercises_by_muscle.get(muscle, [])
            if not available:
                continue
            
            # Pick 2-4 exercises per muscle group
            num_exercises = min(len(available), random.randint(2, 4))
            selected = random.sample(available, num_exercises)
            
            for exercise in selected:
                # Get base weight or random
                base_weight = BASE_WEIGHTS.get(exercise.name, random.randint(10, 40))
                
                # Add progression over time (about 2.5% per month)
                months_ago = day_offset / 30
                progression = 1 + (0.025 * (3 - months_ago))  # Progress from 3 months ago
                current_weight = base_weight * max(0.85, min(1.15, progression))
                
                # Add some daily variation
                current_weight *= random.uniform(0.95, 1.05)
                current_weight = round(current_weight / 2.5) * 2.5  # Round to 2.5kg
                
                if current_weight < 0:
                    current_weight = 0
                
                # Generate 3-5 sets
                num_sets = random.randint(3, 5)
                
                for set_num in range(1, num_sets + 1):
                    # Weight decreases slightly or stays same across sets
                    set_weight = current_weight
                    if set_num > 2 and random.random() < 0.3:
                        set_weight = max(0, current_weight - 2.5)
                    
                    # Reps vary (pyramid or straight sets)
                    if current_weight == 0:  # Bodyweight
                        reps = random.randint(8, 20)
                    else:
                        base_reps = random.randint(6, 12)
                        # Later sets might have fewer reps
                        reps = max(4, base_reps - (set_num - 1) * random.randint(0, 2))
                    
                    Set.objects.create(
                        workout=workout,
                        exercise=exercise,
                        set_number=set_num,
                        weight=Decimal(str(set_weight)),
                        reps=reps,
                        rpe=random.choice([None, None, 7, 7.5, 8, 8, 8.5, 9, 9, 9.5]) if random.random() < 0.4 else None
                    )
                    sets_created += 1
    
    print(f"Created {workouts_created} workouts with {sets_created} sets")
    return workouts_created


def generate_body_weight(user, days=90):
    """Generate body weight entries."""
    print("\nGenerating body weight history...")
    
    today = timezone.now().date()
    
    # Starting weight and goal
    start_weight = random.uniform(75, 85)
    trend = random.choice([-0.5, 0, 0.3])  # Losing, maintaining, or gaining
    
    entries_created = 0
    
    for day_offset in range(days, 0, -1):
        # Log weight 3-5 times per week
        if random.random() < 0.5:
            continue
        
        date = today - timedelta(days=day_offset)
        
        # Weight with trend and daily fluctuation
        months_passed = (days - day_offset) / 30
        weight = start_weight + (trend * months_passed) + random.uniform(-0.8, 0.8)
        weight = round(weight, 1)
        
        BodyWeight.objects.update_or_create(
            user=user,
            date=date,
            defaults={
                'weight': Decimal(str(weight)),
                'notes': random.choice(['', '', '', 'Morning', 'After workout', 'Fasted'])
            }
        )
        entries_created += 1
    
    print(f"Created {entries_created} body weight entries")
    return entries_created


def generate_measurements(user, weeks=12):
    """Generate body measurement entries."""
    print("\nGenerating body measurements...")
    
    today = timezone.now().date()
    
    # Base measurements (in cm)
    base = {
        'chest': random.uniform(95, 105),
        'waist': random.uniform(80, 90),
        'hips': random.uniform(95, 105),
        'left_arm': random.uniform(32, 38),
        'right_arm': random.uniform(32, 38),
        'left_thigh': random.uniform(55, 62),
        'right_thigh': random.uniform(55, 62),
        'left_calf': random.uniform(36, 40),
        'right_calf': random.uniform(36, 40),
        'shoulders': random.uniform(115, 125),
        'neck': random.uniform(38, 42),
    }
    
    entries_created = 0
    
    for week in range(weeks, 0, -1):
        date = today - timedelta(weeks=week)
        
        # Progress over time
        progress_factor = (weeks - week) / weeks
        
        measurement = BodyMeasurement.objects.create(
            user=user,
            date=date,
            chest=round(base['chest'] + progress_factor * 1.5 + random.uniform(-0.5, 0.5), 1),
            waist=round(base['waist'] - progress_factor * 1 + random.uniform(-0.5, 0.5), 1),
            hips=round(base['hips'] + random.uniform(-0.5, 0.5), 1),
            left_arm=round(base['left_arm'] + progress_factor * 0.8 + random.uniform(-0.3, 0.3), 1),
            right_arm=round(base['right_arm'] + progress_factor * 0.8 + random.uniform(-0.3, 0.3), 1),
            left_thigh=round(base['left_thigh'] + progress_factor * 0.5 + random.uniform(-0.3, 0.3), 1),
            right_thigh=round(base['right_thigh'] + progress_factor * 0.5 + random.uniform(-0.3, 0.3), 1),
            left_calf=round(base['left_calf'] + progress_factor * 0.3 + random.uniform(-0.2, 0.2), 1),
            right_calf=round(base['right_calf'] + progress_factor * 0.3 + random.uniform(-0.2, 0.2), 1),
            shoulders=round(base['shoulders'] + progress_factor * 1 + random.uniform(-0.5, 0.5), 1),
            neck=round(base['neck'] + progress_factor * 0.2 + random.uniform(-0.2, 0.2), 1),
        )
        entries_created += 1
    
    print(f"Created {entries_created} measurement entries")
    return entries_created


def generate_goals(user):
    """Generate fitness goals."""
    print("\nGenerating goals...")
    
    today = timezone.now().date()
    
    goals_data = [
        {
            'name': 'Bench Press 100kg',
            'goal_type': 'strength',
            'exercise': Exercise.objects.filter(name='Barbell Bench Press').first(),
            'target_value': 100,
            'target_reps': 1,
            'deadline': today + timedelta(days=90),
        },
        {
            'name': 'Squat 120kg',
            'goal_type': 'strength',
            'exercise': Exercise.objects.filter(name='Back Squat').first(),
            'target_value': 120,
            'target_reps': 5,
            'deadline': today + timedelta(days=60),
        },
        {
            'name': 'Deadlift 140kg',
            'goal_type': 'strength',
            'exercise': Exercise.objects.filter(name='Deadlift').first(),
            'target_value': 140,
            'target_reps': 1,
            'deadline': today + timedelta(days=120),
        },
        {
            'name': '10 Pull-ups',
            'goal_type': 'reps',
            'exercise': Exercise.objects.filter(name='Pull-Up').first(),
            'target_value': 10,
            'deadline': today + timedelta(days=45),
        },
        {
            'name': 'Reach 80kg body weight',
            'goal_type': 'bodyweight',
            'target_value': 80,
            'deadline': today + timedelta(days=60),
        },
    ]
    
    goals_created = 0
    
    for goal_data in goals_data:
        exercise = goal_data.pop('exercise', None)
        goal = Goal.objects.create(
            user=user,
            exercise=exercise,
            **goal_data
        )
        goal.update_progress()
        goals_created += 1
    
    print(f"Created {goals_created} goals")
    return goals_created


def generate_templates(user):
    """Generate workout templates."""
    print("\nGenerating workout templates...")
    
    templates_data = [
        {
            'name': 'Push Day',
            'muscle_groups': 'chest,shoulders,triceps',
            'exercises': [
                ('Barbell Bench Press', 4, '6-8'),
                ('Incline Dumbbell Bench Press', 3, '8-10'),
                ('Overhead Press', 3, '8-10'),
                ('Lateral Raise', 3, '12-15'),
                ('Tricep Pushdown', 3, '10-12'),
            ]
        },
        {
            'name': 'Pull Day',
            'muscle_groups': 'back,biceps',
            'exercises': [
                ('Deadlift', 3, '5'),
                ('Barbell Row', 4, '6-8'),
                ('Lat Pulldown', 3, '8-10'),
                ('Face Pull', 3, '15-20'),
                ('Barbell Curl', 3, '10-12'),
            ]
        },
        {
            'name': 'Leg Day',
            'muscle_groups': 'legs,glutes,calves',
            'exercises': [
                ('Back Squat', 4, '6-8'),
                ('Romanian Deadlift', 3, '8-10'),
                ('Leg Press', 3, '10-12'),
                ('Leg Curl', 3, '10-12'),
                ('Standing Calf Raise', 4, '12-15'),
            ]
        },
        {
            'name': 'Upper Body',
            'muscle_groups': 'chest,back,shoulders,biceps,triceps',
            'exercises': [
                ('Barbell Bench Press', 3, '8-10'),
                ('Barbell Row', 3, '8-10'),
                ('Overhead Press', 3, '8-10'),
                ('Pull-Up', 3, '8-12'),
                ('Dumbbell Curl', 2, '10-12'),
                ('Tricep Pushdown', 2, '10-12'),
            ]
        },
        {
            'name': 'Full Body',
            'muscle_groups': 'chest,back,legs,shoulders',
            'exercises': [
                ('Back Squat', 3, '8'),
                ('Barbell Bench Press', 3, '8'),
                ('Barbell Row', 3, '8'),
                ('Overhead Press', 3, '8'),
                ('Deadlift', 2, '5'),
            ]
        },
    ]
    
    templates_created = 0
    
    for template_data in templates_data:
        template = WorkoutTemplate.objects.create(
            user=user,
            name=template_data['name'],
            muscle_groups=template_data['muscle_groups']
        )
        
        for order, (exercise_name, sets, reps) in enumerate(template_data['exercises']):
            exercise = Exercise.objects.filter(name=exercise_name).first()
            if exercise:
                TemplateExercise.objects.create(
                    template=template,
                    exercise=exercise,
                    order=order,
                    target_sets=sets,
                    target_reps=reps
                )
        
        templates_created += 1
    
    print(f"Created {templates_created} workout templates")
    return templates_created


def clear_demo_data(user):
    """Clear all demo data for user."""
    print("\nClearing existing demo data...")
    
    Workout.objects.filter(user=user).delete()
    BodyWeight.objects.filter(user=user).delete()
    BodyMeasurement.objects.filter(user=user).delete()
    Goal.objects.filter(user=user).delete()
    WorkoutTemplate.objects.filter(user=user).delete()
    
    print("Cleared all existing data for demo user")


def main():
    """Main function to generate all demo data."""
    print("=" * 50)
    print("IronLog Demo Data Generator")
    print("=" * 50)
    
    # Check if exercises exist
    if Exercise.objects.count() == 0:
        print("\nERROR: No exercises found. Please run load_exercises.py first.")
        sys.exit(1)
    
    # Create demo user
    user = create_demo_user()
    
    # Ask to clear existing data
    existing_workouts = Workout.objects.filter(user=user).count()
    if existing_workouts > 0:
        print(f"\nFound {existing_workouts} existing workouts for demo user.")
        response = input("Clear existing data? (y/n): ").strip().lower()
        if response == 'y':
            clear_demo_data(user)
    
    # Generate data
    generate_workouts(user, days=90)
    generate_body_weight(user, days=90)
    generate_measurements(user, weeks=12)
    generate_goals(user)
    generate_templates(user)
    
    print("\n" + "=" * 50)
    print("Demo data generation complete!")
    print("=" * 50)
    print(f"\nLogin credentials:")
    print(f"  Username: demo")
    print(f"  Password: demo123")
    print(f"\nUser ID: {user.profile.tracking_id}")
    print("=" * 50)


if __name__ == '__main__':
    main()
