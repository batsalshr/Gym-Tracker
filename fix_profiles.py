"""Create profiles for existing users who don't have one."""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_tracker.settings')
import django
django.setup()

from django.contrib.auth.models import User
from workouts.models import UserProfile

def create_missing_profiles():
    """Create UserProfile for any users missing one."""
    users_without_profile = []
    
    for user in User.objects.all():
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            users_without_profile.append(user.username)
            print(f"Created profile for: {user.username} (ID: {profile.tracking_id})")
    
    if users_without_profile:
        print(f"\nCreated {len(users_without_profile)} profiles.")
    else:
        print("All users already have profiles.")

if __name__ == '__main__':
    create_missing_profiles()
