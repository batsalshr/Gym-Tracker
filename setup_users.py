"""Setup script to create initial users and migrate data."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_tracker.settings')
django.setup()

from django.contrib.auth.models import User

def create_users():
    """Create admin and Batsal users."""
    
    # Create admin user (superuser)
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@ironlog.com',
            password='admin123'
        )
        print("✓ Created admin user (password: admin123)")
    else:
        print("• Admin user already exists")
    
    # Create Batsal user
    if not User.objects.filter(username='Batsal').exists():
        User.objects.create_user(
            username='Batsal',
            email='batsal@ironlog.com',
            password='Batsal123'
        )
        print("✓ Created Batsal user (password: Batsal123)")
    else:
        print("• Batsal user already exists")

if __name__ == '__main__':
    print("\n=== IronLog User Setup ===\n")
    create_users()
    print("\n=== Setup Complete ===\n")
    print("Users created:")
    print("  1. admin / admin123 (superuser)")
    print("  2. Batsal / Batsal123")
    print("\nYou can now login at http://127.0.0.1:8000/login/")
