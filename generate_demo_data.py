"""
Generate demo data for IronLog gym tracker.
Creates realistic workout history, body weight entries, measurements, and goals.
"""
import os
import sys
import random
from datetime import timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gym_tracker.settings")
import django

django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from workouts.models import (
    Exercise,
    Workout,
    Set,
    BodyWeight,
    BodyMeasurement,
    Goal,
    WorkoutTemplate,
    TemplateExercise,
    UserProfile,
)


def create_demo_user():
    """Create or get demo user."""
    user, created = User.objects.get_or_create(
        username="demo",
        defaults={
            "email": "demo@ironlog.com",
            "first_name": "Demo",
            "last_name": "User",
        },
    )
    if created:
        user.set_password("demo123")
        user.save()
        print("Created demo user: demo / demo123")
    else:
        print("Demo user already exists")

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
        exercises[muscle] = list(
            Exercise.objects.filter(muscle_group=muscle, user__isnull=True)
        )
    return exercises


def generate_workouts(user, days=90):
    """Generate realistic workout history."""
    print(f"\nGenerating {days} days of workout history...")

    exercises_by_muscle = get_exercises_by_muscle()
    today = timezone.now().date()

    SPLITS = {
        "push": ["chest", "shoulders", "triceps"],
        "pull": ["back", "biceps", "forearms"],
        "legs": ["legs", "glutes", "calves"],
        "upper": ["chest", "back", "shoulders", "biceps", "triceps"],
        "lower": ["legs", "glutes", "calves"],
    }

    workout_days = [0, 1, 2, 3, 4]

    BASE_WEIGHTS = {
        "Barbell Bench Press": 60,
        "Deadlift": 80,
        "Back Squat": 70,
        "Overhead Press": 35,
        "Barbell Row": 50,
        "Lat Pulldown": 50,
        "Leg Press": 120,
    }

    workouts_created = 0
    sets_created = 0

    for day_offset in range(days, 0, -1):
        workout_date = today - timedelta(days=day_offset)
        day_of_week = workout_date.weekday()

        if day_of_week not in workout_days:
            continue
        if random.random() < 0.15:
            continue

        if day_of_week == 0:
            split = "push"
        elif day_of_week == 1:
            split = "pull"
        elif day_of_week == 2:
            split = "legs"
        elif day_of_week == 3:
            split = "upper"
        else:
            split = "lower"

        muscle_groups = SPLITS[split]

        workout = Workout.objects.create(
            user=user,
            date=workout_date,
            muscle_groups=",".join(muscle_groups),
            duration_minutes=random.randint(45, 90),
        )
        workouts_created += 1

        for muscle in muscle_groups:
            available = exercises_by_muscle.get(muscle, [])
            if not available:
                continue

            num_exercises = min(len(available), random.randint(2, 4))
            selected = random.sample(available, num_exercises)

            for exercise in selected:
                base_weight = BASE_WEIGHTS.get(exercise.name, random.randint(10, 40))
                months_ago = day_offset / 30
                progression = 1 + (0.025 * (3 - months_ago))
                current_weight = base_weight * max(0.85, min(1.15, progression))
                current_weight *= random.uniform(0.95, 1.05)
                current_weight = round(current_weight / 2.5) * 2.5

                if current_weight < 0:
                    current_weight = 0

                num_sets = random.randint(3, 5)

                for set_num in range(1, num_sets + 1):
                    set_weight = current_weight
                    if set_num > 2 and random.random() < 0.3:
                        set_weight = max(0, current_weight - 2.5)

                    reps = random.randint(6, 12) if current_weight > 0 else random.randint(8, 20)

                    Set.objects.create(
                        workout=workout,
                        exercise=exercise,
                        set_number=set_num,
                        weight=Decimal(str(set_weight)),
                        reps=reps,
                    )
                    sets_created += 1

    print(f"Created {workouts_created} workouts with {sets_created} sets")
    return workouts_created


def generate_body_weight(user, days=90):
    """Generate body weight entries."""
    print("\nGenerating body weight history...")
    today = timezone.now().date()
    start_weight = random.uniform(75, 85)
    trend = random.choice([-0.5, 0, 0.3])
    entries_created = 0

    for day_offset in range(days, 0, -1):
        if random.random() < 0.5:
            continue

        date = today - timedelta(days=day_offset)
        months_passed = (days - day_offset) / 30
        weight = start_weight + (trend * months_passed) + random.uniform(-0.8, 0.8)

        BodyWeight.objects.update_or_create(
            user=user,
            date=date,
            defaults={"weight": Decimal(str(round(weight, 1)))},
        )
        entries_created += 1

    print(f"Created {entries_created} body weight entries")


def generate_goals(user):
    """Generate fitness goals."""
    print("\nGenerating goals...")
    today = timezone.now().date()

    goals = [
        ("Bench Press 100kg", "strength", "Barbell Bench Press", 100, 1, 90),
        ("Squat 120kg", "strength", "Back Squat", 120, 5, 60),
        ("Deadlift 140kg", "strength", "Deadlift", 140, 1, 120),
        ("10 Pull-ups", "reps", "Pull-Up", 10, None, 45),
    ]

    for name, goal_type, exercise_name, target, reps, days_until in goals:
        exercise = Exercise.objects.filter(name=exercise_name).first()
        goal = Goal.objects.create(
            user=user,
            name=name,
            goal_type=goal_type,
            exercise=exercise,
            target_value=target,
            target_reps=reps,
            deadline=today + timedelta(days=days_until),
        )
        goal.update_progress()

    print(f"Created {len(goals)} goals")


def clear_demo_data(user):
    """Clear all demo data for user."""
    print("\nClearing existing demo data...")
    Workout.objects.filter(user=user).delete()
    BodyWeight.objects.filter(user=user).delete()
    BodyMeasurement.objects.filter(user=user).delete()
    Goal.objects.filter(user=user).delete()
    WorkoutTemplate.objects.filter(user=user).delete()
    print("Cleared all existing data")


def main():
    print("=" * 50)
    print("IronLog Demo Data Generator")
    print("=" * 50)

    if Exercise.objects.count() == 0:
        print("\nERROR: No exercises found. Run load_exercises.py first.")
        sys.exit(1)

    user = create_demo_user()

    existing = Workout.objects.filter(user=user).count()
    if existing > 0:
        print(f"\nFound {existing} existing workouts.")
        response = input("Clear existing data? (y/n): ").strip().lower()
        if response == "y":
            clear_demo_data(user)

    generate_workouts(user, days=90)
    generate_body_weight(user, days=90)
    generate_goals(user)

    print("\n" + "=" * 50)
    print("Demo data generation complete!")
    print("Login: demo / demo123")
    print("=" * 50)


if __name__ == "__main__":
    main()
