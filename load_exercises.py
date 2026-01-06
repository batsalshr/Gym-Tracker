#!/usr/bin/env python
"""
Comprehensive Exercise Database Loader

Run this script to populate your database with 300+ exercises.

Usage:
    python load_exercises.py
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_tracker.settings')

import django
django.setup()

from workouts.models import Exercise

# Comprehensive exercise database from user's list
EXERCISES = {
    'chest': [
        # Barbell
        ('Barbell Bench Press', 'barbell'),
        ('Incline Barbell Bench Press', 'barbell'),
        ('Decline Barbell Bench Press', 'barbell'),
        ('Close-Grip Barbell Bench Press', 'barbell'),
        ('Reverse-Grip Barbell Bench Press', 'barbell'),
        ('Guillotine Press', 'barbell'),
        ('Barbell Pullover', 'barbell'),
        
        # Dumbbell
        ('Dumbbell Bench Press', 'dumbbell'),
        ('Incline Dumbbell Bench Press', 'dumbbell'),
        ('Decline Dumbbell Bench Press', 'dumbbell'),
        ('Dumbbell Fly', 'dumbbell'),
        ('Incline Dumbbell Fly', 'dumbbell'),
        ('Decline Dumbbell Fly', 'dumbbell'),
        ('Dumbbell Pullover', 'dumbbell'),
        ('Dumbbell Squeeze Press', 'dumbbell'),
        ('Dumbbell Floor Press', 'dumbbell'),
        ('Single-Arm Dumbbell Bench Press', 'dumbbell'),
        
        # Cable
        ('Cable Crossover', 'cable'),
        ('High-to-Low Cable Fly', 'cable'),
        ('Low-to-High Cable Fly', 'cable'),
        ('Cable Chest Press', 'cable'),
        ('Single-Arm Cable Fly', 'cable'),
        
        # Machine
        ('Seated Chest Press Machine', 'machine'),
        ('Incline Chest Press Machine', 'machine'),
        ('Decline Chest Press Machine', 'machine'),
        ('Pec Deck', 'machine'),
        ('Smith Machine Bench Press', 'machine'),
        
        # Bodyweight
        ('Push-Up', 'bodyweight'),
        ('Wide-Grip Push-Up', 'bodyweight'),
        ('Diamond Push-Up', 'bodyweight'),
        ('Incline Push-Up', 'bodyweight'),
        ('Decline Push-Up', 'bodyweight'),
        ('Chest Dip', 'bodyweight'),
        ('Weighted Dip', 'bodyweight'),
        ('Bench Dip', 'bodyweight'),
        ('Plyometric Push-Up', 'bodyweight'),
        ('One-Arm Push-Up', 'bodyweight'),
        ('Fingertip Push-Up', 'bodyweight'),
    ],
    
    'back': [
        # Barbell
        ('Deadlift', 'barbell'),
        ('Sumo Deadlift', 'barbell'),
        ('Stiff-Leg Deadlift', 'barbell'),
        ('Romanian Deadlift', 'barbell'),
        ('Rack Pull', 'barbell'),
        ('Barbell Bent-Over Row', 'barbell'),
        ('Pendlay Row', 'barbell'),
        ('Yates Row', 'barbell'),
        ('T-Bar Row', 'barbell'),
        ('Barbell Upright Row', 'barbell'),
        ('Barbell Shrug', 'barbell'),
        ('Good Morning', 'barbell'),
        
        # Dumbbell
        ('One-Arm Dumbbell Row', 'dumbbell'),
        ('Dumbbell Bent-Over Row', 'dumbbell'),
        ('Chest-Supported Dumbbell Row', 'dumbbell'),
        ('Dumbbell Shrug', 'dumbbell'),
        ('Dumbbell Upright Row', 'dumbbell'),
        ('Dumbbell Pullover', 'dumbbell'),
        ('Dumbbell Deadlift', 'dumbbell'),
        ("Farmer's Walk", 'dumbbell'),
        
        # Cable
        ('Lat Pulldown', 'cable'),
        ('Wide-Grip Lat Pulldown', 'cable'),
        ('Close-Grip Lat Pulldown', 'cable'),
        ('Reverse-Grip Lat Pulldown', 'cable'),
        ('Seated Cable Row', 'cable'),
        ('Wide-Grip Cable Row', 'cable'),
        ('Neutral-Grip Cable Row', 'cable'),
        ('Straight-Arm Pulldown', 'cable'),
        ('Face Pull', 'cable'),
        ('Cable Pullover', 'cable'),
        ('Cable High Row', 'cable'),
        
        # Machine
        ('Assisted Pull-Up Machine', 'machine'),
        ('Seated Row Machine', 'machine'),
        ('T-Bar Row Machine', 'machine'),
        ('High Row Machine', 'machine'),
        ('Low Row Machine', 'machine'),
        ('Lower Back Extension Machine', 'machine'),
        ('Pullover Machine', 'machine'),
        
        # Bodyweight
        ('Pull-Up', 'bodyweight'),
        ('Chin-Up', 'bodyweight'),
        ('Neutral-Grip Pull-Up', 'bodyweight'),
        ('Inverted Row', 'bodyweight'),
        ('Back Extension', 'bodyweight'),
        ('Superman', 'bodyweight'),
        ('Scapular Pull-Up', 'bodyweight'),
    ],
    
    'legs': [
        # Barbell
        ('Back Squat', 'barbell'),
        ('High-Bar Squat', 'barbell'),
        ('Low-Bar Squat', 'barbell'),
        ('Box Squat', 'barbell'),
        ('Pause Squat', 'barbell'),
        ('Front Squat', 'barbell'),
        ('Overhead Squat', 'barbell'),
        ('Barbell Lunge', 'barbell'),
        ('Reverse Barbell Lunge', 'barbell'),
        ('Walking Barbell Lunge', 'barbell'),
        ('Bulgarian Split Squat', 'barbell'),
        ('Barbell Step-Up', 'barbell'),
        ('Barbell Hip Thrust', 'barbell'),
        ('Barbell Glute Bridge', 'barbell'),
        ('Barbell Hack Squat', 'barbell'),
        ('Barbell Calf Raise', 'barbell'),
        
        # Dumbbell
        ('Dumbbell Squat', 'dumbbell'),
        ('Goblet Squat', 'dumbbell'),
        ('Dumbbell Lunge', 'dumbbell'),
        ('Reverse Dumbbell Lunge', 'dumbbell'),
        ('Walking Dumbbell Lunge', 'dumbbell'),
        ('Lateral Lunge', 'dumbbell'),
        ('Dumbbell Bulgarian Split Squat', 'dumbbell'),
        ('Dumbbell Step-Up', 'dumbbell'),
        ('Dumbbell Romanian Deadlift', 'dumbbell'),
        ('Dumbbell Stiff-Leg Deadlift', 'dumbbell'),
        ('Single-Leg Romanian Deadlift', 'dumbbell'),
        ('Dumbbell Hip Thrust', 'dumbbell'),
        ('Dumbbell Glute Bridge', 'dumbbell'),
        ('Dumbbell Calf Raise', 'dumbbell'),
        
        # Cable
        ('Cable Pull-Through', 'cable'),
        ('Cable Glute Kickback', 'cable'),
        ('Cable Hip Abduction', 'cable'),
        ('Cable Hip Adduction', 'cable'),
        ('Cable Leg Curl', 'cable'),
        ('Cable Leg Extension', 'cable'),
        
        # Machine
        ('Leg Press', 'machine'),
        ('Hack Squat Machine', 'machine'),
        ('Smith Machine Squat', 'machine'),
        ('Leg Extension', 'machine'),
        ('Lying Leg Curl', 'machine'),
        ('Seated Leg Curl', 'machine'),
        ('Glute Ham Raise', 'machine'),
        ('Hip Thrust Machine', 'machine'),
        ('Seated Calf Raise', 'machine'),
        ('Standing Calf Raise', 'machine'),
        ('Inner Thigh Machine', 'machine'),
        ('Outer Thigh Machine', 'machine'),
        ('Reverse Hyperextension', 'machine'),
        
        # Bodyweight
        ('Bodyweight Squat', 'bodyweight'),
        ('Wall Sit', 'bodyweight'),
        ('Lunge', 'bodyweight'),
        ('Reverse Lunge', 'bodyweight'),
        ('Walking Lunge', 'bodyweight'),
        ('Step-Up', 'bodyweight'),
        ('Pistol Squat', 'bodyweight'),
        ('Split Squat', 'bodyweight'),
        ('Glute Bridge', 'bodyweight'),
        ('Hip Thrust', 'bodyweight'),
        ('Nordic Hamstring Curl', 'bodyweight'),
        ('Calf Raise', 'bodyweight'),
        ('Box Jump', 'bodyweight'),
        ('Broad Jump', 'bodyweight'),
    ],
    
    'shoulders': [
        # Barbell
        ('Overhead Press', 'barbell'),
        ('Military Press', 'barbell'),
        ('Push Press', 'barbell'),
        ('Behind-the-Neck Press', 'barbell'),
        ('Landmine Press', 'barbell'),
        ('Barbell Upright Row', 'barbell'),
        ('Barbell Front Raise', 'barbell'),
        ('Barbell Shrug', 'barbell'),
        ('Bradford Press', 'barbell'),
        
        # Dumbbell
        ('Dumbbell Shoulder Press', 'dumbbell'),
        ('Arnold Press', 'dumbbell'),
        ('Dumbbell Lateral Raise', 'dumbbell'),
        ('Leaning Lateral Raise', 'dumbbell'),
        ('Seated Lateral Raise', 'dumbbell'),
        ('Dumbbell Front Raise', 'dumbbell'),
        ('Dumbbell Rear Delt Fly', 'dumbbell'),
        ('Dumbbell Upright Row', 'dumbbell'),
        ('Dumbbell Shrug', 'dumbbell'),
        ('Y Raise', 'dumbbell'),
        ('T Raise', 'dumbbell'),
        ('External Rotation', 'dumbbell'),
        ('Internal Rotation', 'dumbbell'),
        
        # Cable
        ('Cable Lateral Raise', 'cable'),
        ('Cable Front Raise', 'cable'),
        ('Cable Rear Delt Fly', 'cable'),
        ('Face Pull', 'cable'),
        ('Cable Upright Row', 'cable'),
        ('Cable Shoulder Press', 'cable'),
        ('Cable Shrug', 'cable'),
        
        # Machine
        ('Machine Shoulder Press', 'machine'),
        ('Smith Machine Overhead Press', 'machine'),
        ('Lateral Raise Machine', 'machine'),
        ('Rear Delt Fly Machine', 'machine'),
        ('Shrug Machine', 'machine'),
        
        # Bodyweight
        ('Handstand Push-Up', 'bodyweight'),
        ('Pike Push-Up', 'bodyweight'),
        ('Elevated Pike Push-Up', 'bodyweight'),
    ],
    
    'biceps': [
        # Barbell
        ('Barbell Curl', 'barbell'),
        ('EZ-Bar Curl', 'barbell'),
        ('Wide-Grip Barbell Curl', 'barbell'),
        ('Close-Grip Barbell Curl', 'barbell'),
        ('Barbell Preacher Curl', 'barbell'),
        ('Drag Curl', 'barbell'),
        ('Reverse Barbell Curl', 'barbell'),
        ('Barbell Spider Curl', 'barbell'),
        ('21s', 'barbell'),
        
        # Dumbbell
        ('Dumbbell Curl', 'dumbbell'),
        ('Alternating Dumbbell Curl', 'dumbbell'),
        ('Seated Dumbbell Curl', 'dumbbell'),
        ('Hammer Curl', 'dumbbell'),
        ('Cross-Body Hammer Curl', 'dumbbell'),
        ('Incline Dumbbell Curl', 'dumbbell'),
        ('Concentration Curl', 'dumbbell'),
        ('Dumbbell Preacher Curl', 'dumbbell'),
        ('Zottman Curl', 'dumbbell'),
        ('Dumbbell Spider Curl', 'dumbbell'),
        
        # Cable
        ('Cable Curl', 'cable'),
        ('Rope Curl', 'cable'),
        ('Cable Preacher Curl', 'cable'),
        ('Overhead Cable Curl', 'cable'),
        ('One-Arm Cable Curl', 'cable'),
        ('Reverse Cable Curl', 'cable'),
        
        # Machine
        ('Bicep Curl Machine', 'machine'),
        
        # Bodyweight
        ('Chin-Up', 'bodyweight'),
        ('Suspension Curl', 'bodyweight'),
    ],
    
    'triceps': [
        # Barbell
        ('Close-Grip Bench Press', 'barbell'),
        ('Skullcrusher', 'barbell'),
        ('EZ-Bar Skullcrusher', 'barbell'),
        ('Incline Skullcrusher', 'barbell'),
        ('Decline Skullcrusher', 'barbell'),
        ('Overhead Triceps Extension', 'barbell'),
        ('JM Press', 'barbell'),
        ('Floor Press', 'barbell'),
        
        # Dumbbell
        ('Dumbbell Lying Triceps Extension', 'dumbbell'),
        ('Overhead Dumbbell Triceps Extension', 'dumbbell'),
        ('Single-Arm Overhead Dumbbell Extension', 'dumbbell'),
        ('Triceps Kickback', 'dumbbell'),
        ('Tate Press', 'dumbbell'),
        ('Dumbbell Close-Grip Press', 'dumbbell'),
        
        # Cable
        ('Cable Pushdown', 'cable'),
        ('Rope Pushdown', 'cable'),
        ('Straight-Bar Pushdown', 'cable'),
        ('V-Bar Pushdown', 'cable'),
        ('Reverse-Grip Pushdown', 'cable'),
        ('Cable Overhead Triceps Extension', 'cable'),
        ('Cable Triceps Kickback', 'cable'),
        ('Cable Skullcrusher', 'cable'),
        
        # Machine
        ('Dip Machine', 'machine'),
        ('Triceps Extension Machine', 'machine'),
        
        # Bodyweight
        ('Dip', 'bodyweight'),
        ('Bench Dip', 'bodyweight'),
        ('Diamond Push-Up', 'bodyweight'),
        ('Bodyweight Triceps Extension', 'bodyweight'),
    ],
    
    'forearms': [
        # Barbell
        ('Wrist Curl', 'barbell'),
        ('Reverse Wrist Curl', 'barbell'),
        ('Behind-the-Back Wrist Curl', 'barbell'),
        
        # Other
        ('Plate Pinch', 'other'),
        ('Wrist Roller', 'other'),
        ('Grip Gripper', 'other'),
        ('Towel Pull-Up', 'bodyweight'),
        ('Fat Grip Training', 'other'),
    ],
    
    'core': [
        # Bodyweight
        ('Crunch', 'bodyweight'),
        ('Reverse Crunch', 'bodyweight'),
        ('Twisting Crunch', 'bodyweight'),
        ('Bicycle Crunch', 'bodyweight'),
        ('Sit-Up', 'bodyweight'),
        ('Leg Raise', 'bodyweight'),
        ('Hanging Knee Raise', 'bodyweight'),
        ('Hanging Leg Raise', 'bodyweight'),
        ('Toes-to-Bar', 'bodyweight'),
        ('Plank', 'bodyweight'),
        ('Side Plank', 'bodyweight'),
        ('Mountain Climber', 'bodyweight'),
        ('V-Up', 'bodyweight'),
        ('Dragon Flag', 'bodyweight'),
        ('Flutter Kicks', 'bodyweight'),
        ('Scissor Kicks', 'bodyweight'),
        ('Russian Twist', 'bodyweight'),
        ('Windshield Wipers', 'bodyweight'),
        ('Back Extension', 'bodyweight'),
        
        # Weighted
        ('Weighted Crunch', 'other'),
        ('Decline Sit-Up', 'machine'),
        
        # Cable
        ('Cable Crunch', 'cable'),
        ('Woodchopper', 'cable'),
        ('Cable Side Bend', 'cable'),
        ('Pallof Press', 'cable'),
        
        # Dumbbell
        ('Dumbbell Side Bend', 'dumbbell'),
        
        # Other
        ('Ab Rollout', 'other'),
        ('Ab Wheel Rollout', 'other'),
        ('Landmine Twist', 'barbell'),
    ],
    
    'cardio': [
        # Machine
        ('Treadmill Running', 'machine'),
        ('Treadmill Walking', 'machine'),
        ('Treadmill Incline Walk', 'machine'),
        ('Elliptical', 'machine'),
        ('Stationary Bike', 'machine'),
        ('Recumbent Bike', 'machine'),
        ('Rowing Machine', 'machine'),
        ('Stair Climber', 'machine'),
        ('Assault Bike', 'machine'),
        ('Ski Erg', 'machine'),
        
        # Bodyweight/Outdoor
        ('Running', 'bodyweight'),
        ('Jogging', 'bodyweight'),
        ('Sprints', 'bodyweight'),
        ('Jump Rope', 'bodyweight'),
        ('Jumping Jacks', 'bodyweight'),
        ('Burpees', 'bodyweight'),
        ('High Knees', 'bodyweight'),
        ('Box Jump', 'bodyweight'),
        ('Swimming', 'bodyweight'),
        ('Cycling', 'bodyweight'),
        ('Walking', 'bodyweight'),
        ('Hiking', 'bodyweight'),
        
        # Other
        ('Battle Ropes', 'other'),
        ('Sled Push', 'other'),
        ('Sled Pull', 'other'),
        ('Kettlebell Swings', 'other'),
    ],
    
    'glutes': [
        # Barbell
        ('Barbell Hip Thrust', 'barbell'),
        ('Barbell Glute Bridge', 'barbell'),
        ('Sumo Squat', 'barbell'),
        
        # Dumbbell
        ('Dumbbell Hip Thrust', 'dumbbell'),
        ('Single-Leg Hip Thrust', 'dumbbell'),
        ('Dumbbell Glute Bridge', 'dumbbell'),
        
        # Cable
        ('Cable Pull-Through', 'cable'),
        ('Cable Kickback', 'cable'),
        ('Cable Glute Kickback', 'cable'),
        
        # Machine
        ('Hip Thrust Machine', 'machine'),
        ('Glute Drive', 'machine'),
        ('Glute Kickback Machine', 'machine'),
        
        # Bodyweight
        ('Glute Bridge', 'bodyweight'),
        ('Single-Leg Glute Bridge', 'bodyweight'),
        ('Donkey Kick', 'bodyweight'),
        ('Fire Hydrant', 'bodyweight'),
        ('Frog Pump', 'bodyweight'),
        ('Clamshell', 'bodyweight'),
    ],
    
    'calves': [
        # Machine
        ('Standing Calf Raise', 'machine'),
        ('Seated Calf Raise', 'machine'),
        ('Leg Press Calf Raise', 'machine'),
        ('Donkey Calf Raise', 'machine'),
        
        # Dumbbell
        ('Dumbbell Calf Raise', 'dumbbell'),
        ('Single-Leg Dumbbell Calf Raise', 'dumbbell'),
        
        # Bodyweight
        ('Bodyweight Calf Raise', 'bodyweight'),
        ('Single-Leg Calf Raise', 'bodyweight'),
    ],
    
    'traps': [
        # Barbell
        ('Barbell Shrug', 'barbell'),
        ('Snatch-Grip Shrug', 'barbell'),
        ('Barbell Upright Row', 'barbell'),
        
        # Dumbbell
        ('Dumbbell Shrug', 'dumbbell'),
        ('Incline Dumbbell Shrug', 'dumbbell'),
        
        # Cable
        ('Cable Shrug', 'cable'),
        
        # Machine
        ('Machine Shrug', 'machine'),
        ('Smith Machine Shrug', 'machine'),
    ],
}


def load_exercises():
    """Load all exercises into the database."""
    total_created = 0
    total_updated = 0
    
    for muscle_group, exercises in EXERCISES.items():
        for exercise_data in exercises:
            name = exercise_data[0]
            equipment = exercise_data[1] if len(exercise_data) > 1 else ''
            
            exercise, created = Exercise.objects.update_or_create(
                name=name,
                muscle_group=muscle_group,
                defaults={'equipment': equipment}
            )
            
            if created:
                total_created += 1
            else:
                total_updated += 1
    
    return total_created, total_updated


def main():
    print("\n🏋️ Loading Exercise Database...\n")
    print("-" * 40)
    
    created, updated = load_exercises()
    
    print(f"✓ Created {created} new exercises")
    print(f"✓ Updated {updated} existing exercises")
    print(f"✓ Total: {Exercise.objects.count()} exercises\n")
    
    # Print summary by muscle group
    print("Exercises by muscle group:")
    for muscle_group, _ in Exercise.MUSCLE_GROUPS:
        count = Exercise.objects.filter(muscle_group=muscle_group).count()
        if count > 0:
            print(f"  {muscle_group.capitalize()}: {count}")
    
    print("-" * 40)
    print("\n✅ Exercise database loaded successfully!\n")


if __name__ == '__main__':
    main()