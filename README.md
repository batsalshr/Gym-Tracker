# 💪 Gym Tracker

A local Django application for tracking gym workouts and personal bests. Designed for personal use on your laptop with SQLite database storage.

## Features

- **Exercise Management**: Create and manage exercises with muscle group categorization
- **Workout Sessions**: Log workouts with multiple sets per exercise
- **Personal Bests**: Track your PRs by heaviest weight or highest reps
- **Progression Suggestions**: Get automatic recommendations for weight increases
- **Simple UI**: Clean, responsive interface using Django templates
- **Fully Local**: No external dependencies, runs entirely on localhost

## Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### 2. Installation

```bash
# Clone or download the project
cd gym_tracker

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup (creates database and optional sample exercises)
python setup.py

# Start the server
python manage.py runserver
```

### 3. Access the App

Open your browser and go to: **http://localhost:8000**

## Project Structure

```
gym_tracker/
├── gym_tracker/           # Django project settings
│   ├── settings.py        # Configuration (SQLite, localhost only)
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI entry point
├── workouts/              # Main application
│   ├── models.py          # Exercise, WorkoutSession, Set models
│   ├── views.py           # All views (dashboard, sessions, exercises, PBs)
│   ├── forms.py           # Django forms
│   ├── urls.py            # App URL patterns
│   └── admin.py           # Django admin configuration
├── templates/             # HTML templates
│   ├── base.html          # Base template with navigation
│   └── workouts/          # App-specific templates
├── manage.py              # Django management script
├── setup.py               # Initial setup script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Models

### Exercise
- `name`: Exercise name (unique)
- `description`: Optional description
- `muscle_group`: Primary muscle group targeted
- **Methods**:
  - `get_personal_best_weight()`: Returns highest weight set
  - `get_personal_best_reps()`: Returns highest reps set
  - `get_suggested_progression()`: Calculates next weight target

### WorkoutSession
- `date`: Date of workout
- `notes`: Optional session notes
- `duration_minutes`: Optional duration
- **Methods**:
  - `get_exercises_performed()`: List unique exercises
  - `get_total_volume()`: Sum of weight × reps
  - `get_sets_by_exercise()`: Sets grouped by exercise

### Set
- `session`: Foreign key to WorkoutSession
- `exercise`: Foreign key to Exercise
- `weight`: Weight in kg (decimal)
- `reps`: Number of repetitions
- `notes`: Optional notes
- **Methods**:
  - `get_volume()`: weight × reps
  - `is_personal_best()`: Check if this is a PR

## Usage Guide

### Adding Exercises

1. Go to **Exercises** in the navigation
2. Click **+ Add Exercise**
3. Fill in the name, muscle group, and description
4. Or click a suggested exercise to quick-fill

### Logging a Workout

1. Click **+ New Workout** in the navigation
2. Set the date and optional duration/notes
3. Add sets:
   - Select exercise from dropdown
   - Enter weight (kg) and reps
   - The weight field auto-fills with progression suggestion
   - Add notes if needed
4. Click **+ Add Set** for more rows
5. Save the workout

### Viewing Personal Bests

1. Go to **Personal Bests** in the navigation
2. Toggle between **By Weight** and **By Reps** views
3. See your best lifts and suggested next targets

### Progression System

The app suggests weight increases based on your last workout:
- **8+ reps**: Suggest +2.5kg increase
- **5-7 reps**: Stay at same weight, aim for more reps
- **< 5 reps**: Consider reducing weight for better form

## Django Admin

Access the admin interface at http://localhost:8000/admin/

To create a superuser:
```bash
python manage.py createsuperuser
```

## API Endpoints

The app includes simple API endpoints for AJAX functionality:

- `GET /api/exercises/search/?q=<query>`: Search exercises
- `GET /api/exercises/<id>/progression/`: Get progression suggestion

## Customization

### Change Weight Increments

Edit `workouts/models.py`, `Exercise.get_suggested_progression()`:
```python
suggested_weight = current_weight + Decimal('2.5')  # Change this value
```

### Add More Fields

The models are designed to be easily extended. Add fields to models.py and run:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Backup Your Data

Your workout data is stored in `db.sqlite3`. To backup:
```bash
cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
```

## License

This project is for personal use. Feel free to modify and adapt it to your needs.

---

**Happy lifting! 🏋️**
