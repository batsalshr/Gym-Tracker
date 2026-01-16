# IronLog - Gym Workout Tracker

A modern, full-featured workout tracking application built with Django. Track your exercises, monitor progress, set goals, and analyze your training with beautiful charts and insights.

---

## Features

### Core Tracking
- Log workouts with multiple exercises and sets
- Track weight, reps, and RPE for each set
- Automatic personal best detection
- Weight suggestions based on previous performance
- Workout templates for quick logging

### Analytics
- Weekly volume and frequency charts
- Muscle group distribution
- Body weight trends
- Training insights (streaks, best days, favorites)
- Estimated 1RM calculations

### Progress Tools
- Personal records tracking with rankings
- Goal setting and progress monitoring
- Body measurements tracking
- Achievement system

### Exercise Library
- 336 pre-loaded exercises with descriptions
- Step-by-step instructions for proper form
- Muscle activation visualization
- Equipment and movement type info
- Searchable and filterable

### User System
- Multi-user support with authentication
- Unique tracking IDs for each user
- Customizable profiles with avatars
- Display names and bios

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Extract the project files:
```bash
unzip gym_tracker.zip
cd gym_tracker
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

3. Install dependencies:
```bash
pip install django
```

4. Initialize the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Load exercise data:
```bash
python load_exercises.py
python populate_exercise_details.py
```

6. Create an admin user:
```bash
python manage.py createsuperuser
```

7. Start the server:
```bash
python manage.py runserver
```

8. Open your browser:
```
http://127.0.0.1:8000
```

---

## Quick Start Commands

Run all setup in one go:
```bash
cd gym_tracker
python -m venv venv
source venv/bin/activate
pip install django
python manage.py makemigrations
python manage.py migrate
python load_exercises.py
python populate_exercise_details.py
python manage.py createsuperuser
python manage.py runserver
```

---

## Project Structure

```
gym_tracker/
├── gym_tracker/            # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── workouts/               # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── urls.py             # URL routing
│   └── migrations/         # Database migrations
├── templates/              # HTML templates
│   ├── base.html           # Base layout
│   ├── registration/       # Auth templates
│   └── workouts/           # App templates
├── load_exercises.py       # Exercise data loader
├── populate_exercise_details.py  # Exercise descriptions
└── manage.py               # Django CLI
```

---

## Database Models

### UserProfile
- Extends Django User model
- Unique tracking ID (IL-XXXXXX format)
- Display name, bio, avatar color
- Workout statistics

### Exercise
- Name, muscle group, equipment
- Description and instructions
- Personal best tracking methods

### Workout
- Date, duration, notes
- Training type classification
- Linked sets and exercises

### Set
- Weight, reps, RPE
- Linked to workout and exercise
- Supports rest time tracking

### Goal
- Target weight, reps, or volume
- Progress tracking
- Deadline support

### BodyWeight / BodyMeasurement
- Date-stamped entries
- Trend visualization

---

## Pages Overview

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | / | Overview with recent activity |
| Log Workout | /log/ | Create new workout |
| History | /history/ | Browse past workouts |
| Exercises | /exercises/ | Exercise library |
| Exercise Detail | /exercises/{id}/progress/ | Stats for specific exercise |
| Personal Bests | /pbs/ | All-time records |
| Goals | /goals/ | Goal management |
| Charts | /charts/ | Analytics dashboard |
| Calendar | /calendar/ | Monthly workout view |
| Body Weight | /bodyweight/ | Weight tracking |
| Measurements | /measurements/ | Body measurements |
| Achievements | /achievements/ | Unlocked badges |
| Calculator | /calculator/ | 1RM calculator |
| Templates | /templates/ | Workout templates |
| Profile | /profile/ | User settings |

---

## Configuration

### Settings (gym_tracker/settings.py)

Debug mode:
```python
DEBUG = True  # Set to False in production
```

Allowed hosts:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

Database (default SQLite):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

## API Endpoints

### Exercise Suggestion
```
GET /api/exercise/{id}/suggestion/
```
Returns weight suggestion based on history.

### Exercise Search
```
GET /api/exercises/search/?q={query}&groups={muscle_groups}
```
Returns matching exercises for autocomplete.

---

## Customization

### Adding Exercises
Add entries to load_exercises.py and run:
```bash
python load_exercises.py
```

### Adding Exercise Instructions
Add entries to populate_exercise_details.py and run:
```bash
python populate_exercise_details.py
```

### Styling
- CSS variables defined in templates/base.html
- Dark theme with blue accent colors
- Font Awesome 6.5.1 for icons

---

## Tech Stack

- Backend: Django 4.x
- Database: SQLite (default)
- Frontend: HTML, CSS, JavaScript
- Charts: Chart.js
- Icons: Font Awesome 6.5.1
- Styling: Custom CSS with CSS variables

---

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

---

## Troubleshooting

### Migration errors
```bash
python manage.py makemigrations workouts
python manage.py migrate
```

### Missing exercises
```bash
python load_exercises.py
python populate_exercise_details.py
```

### Reset database
```bash
rm db.sqlite3
python manage.py migrate
python load_exercises.py
python populate_exercise_details.py
python manage.py createsuperuser
```

### Port already in use
```bash
python manage.py runserver 8080
```

---

## License

This project is for personal use.

---

## Version

Current: 1.0.0

Last Updated: January 2025
