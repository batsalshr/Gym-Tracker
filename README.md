# 💪 GymTracker

A clean, modern Django app for tracking your gym workouts and personal bests.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Django](https://img.shields.io/badge/Django-4.2-green)

## ✨ Features

- **Step-by-step workout logging** - Easy 3-step flow to log workouts
- **Day type selection** - Chest Day, Back Day, Push/Pull, Full Body, etc.
- **Smart weight suggestions** - Automatically suggests next weight based on your last performance
- **Personal bests tracking** - See your PRs for each exercise
- **Clean, modern UI** - Beautiful gradient design that works on desktop and mobile
- **Fully local** - All data stored locally in SQLite

## 🚀 Quick Start

```bash
# 1. Navigate to the project
cd gym_tracker

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Django
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Start the server
python manage.py runserver
```

Then open **http://localhost:8000** in your browser!

## 📱 Workflow

### Logging a Workout

**Step 1: Select Day Type**
- Choose what you're training (Chest Day, Leg Day, Push Day, etc.)
- Set the date (defaults to today)

**Step 2: Add Exercise**  
- Select an exercise from the dropdown (organized by muscle group)
- Choose number of sets (default: 3)
- See weight suggestions based on your last workout

**Step 3: Enter Sets**
- Enter weight (kg) and reps for each set
- Add optional notes
- Save and add more exercises, or finish workout

### Example

```
Day: Chest Day
Date: Today

Exercise: Bench Press (3 sets)
├── Set 1: 60kg × 10 reps
├── Set 2: 65kg × 8 reps  
└── Set 3: 70kg × 6 reps

Exercise: Incline Bench (3 sets)
├── Set 1: 50kg × 10 reps
├── Set 2: 55kg × 8 reps
└── Set 3: 55kg × 7 reps

→ Save Workout ✓
```

## 📊 Features in Detail

### Dashboard
- Total workouts and sets count
- This week's workout count
- Recent workouts with quick access
- Top 5 personal bests

### Personal Bests
- View all PRs sorted by weight or reps
- See next suggested weight
- Track when you hit each PR

### Progression System
The app suggests weight increases based on your performance:
- **8+ reps** → Add 2.5kg next time 📈
- **5-7 reps** → Stay at current weight
- **< 5 reps** → Consider reducing weight

## 🏗️ Project Structure

```
gym_tracker/
├── gym_tracker/          # Django project config
│   ├── settings.py       # Settings (SQLite, localhost)
│   └── urls.py           # Main URL routing
├── workouts/             # Main app
│   ├── models.py         # Exercise, Workout, Set models
│   ├── views.py          # All views
│   ├── urls.py           # App URLs
│   └── admin.py          # Admin config
├── templates/            # HTML templates
│   ├── base.html         # Base template with styling
│   └── workouts/         # App templates
├── manage.py
└── requirements.txt
```

## 📦 Models

### Exercise
- `name` - Exercise name
- `muscle_group` - Chest, Back, Shoulders, Legs, Biceps, Triceps, Core

### Workout
- `date` - Workout date
- `day_type` - Chest Day, Back Day, Push, Pull, Upper, Lower, Full Body
- `notes` - Optional notes

### Set
- `workout` - Link to workout
- `exercise` - Link to exercise
- `set_number` - Set number (1, 2, 3...)
- `weight` - Weight in kg
- `reps` - Number of reps
- `notes` - Optional notes

## 🎨 UI

The app features a modern, gradient-based design with:
- Responsive layout for mobile and desktop
- Card-based components
- Clear visual hierarchy
- Emoji icons for quick recognition

## 💾 Data Backup

Your data is stored in `db.sqlite3`. To backup:

```bash
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3
```

## 🔧 Customization

### Add More Day Types
Edit `workouts/models.py`:
```python
DAY_TYPES = [
    ('chest', 'Chest Day'),
    ('arms', 'Arms Day'),  # Add new type
    # ...
]
```

Then run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Change Weight Increment
Edit `workouts/models.py` in the `get_suggested_weight` method:
```python
return last.weight + Decimal('2.5')  # Change to 1.25 or 5.0
```

---

**Happy lifting! 🏋️**
