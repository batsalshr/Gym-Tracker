# 💪 Gym Tracker

A clean, modern Django app for tracking gym workouts and personal bests. Features a vibey sidebar UI with smooth UX.

## ✨ Features

- **Dashboard** - Welcome banner, weekly stats, recent workouts, key PRs
- **Log Workout** - Two-step flow: select type → add exercises with sets
- **History** - View all past workouts with expandable details
- **Personal Bests** - Track PRs by weight or reps with progression suggestions
- **Exercise Library** - Manage your exercises by muscle group
- **Smart Suggestions** - Auto-suggests weight based on last performance

## 🎨 Design

- Vibrant blue accent (#3A86FF)
- Soft gray backgrounds
- Fixed sidebar navigation
- Card-based layout with subtle shadows
- Clean, Inter font typography

## 🚀 Quick Start

```bash
# 1. Navigate to project
cd gym_tracker

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Django
pip install -r requirements.txt

# 4. Run migrations
python3 manage.py migrate

# 5. (Optional) Add sample exercises
python3 manage.py shell -c "
from workouts.models import Exercise
exercises = [
    ('Bench Press', 'chest'), ('Incline Bench Press', 'chest'), ('Dumbbell Fly', 'chest'),
    ('Deadlift', 'back'), ('Barbell Row', 'back'), ('Lat Pulldown', 'back'), ('Pull-up', 'back'),
    ('Squat', 'legs'), ('Leg Press', 'legs'), ('Leg Curl', 'legs'), ('Romanian Deadlift', 'legs'),
    ('Overhead Press', 'shoulders'), ('Lateral Raise', 'shoulders'), ('Face Pull', 'shoulders'),
    ('Barbell Curl', 'biceps'), ('Dumbbell Curl', 'biceps'), ('Hammer Curl', 'biceps'),
    ('Tricep Pushdown', 'triceps'), ('Skull Crusher', 'triceps'), ('Dip', 'triceps'),
]
for name, muscle in exercises:
    Exercise.objects.get_or_create(name=name, muscle_group=muscle)
print(f'Created {Exercise.objects.count()} exercises')
"

# 6. Start server
python3 manage.py runserver
```

Open **http://127.0.0.1:8000**

## 📱 Workflow

### Logging a Workout

1. **Dashboard** → Click "Log New Workout"
2. **Step 1** → Select workout type (Chest, Back, Push, Pull, etc.) and date
3. **Step 2** → Add exercises:
   - Select exercise from dropdown
   - See weight suggestion based on last workout
   - Enter weight/reps for each set
   - Save & add more, or finish

### Progression System

The app suggests weights based on your last performance:
- **8+ reps** → Add 2.5kg next time 📈
- **5-7 reps** → Keep same weight
- **< 5 reps** → Consider reducing

## 📁 Project Structure

```
gym_tracker/
├── gym_tracker/          # Django config
│   ├── settings.py
│   └── urls.py
├── workouts/             # Main app
│   ├── models.py         # Exercise, Workout, Set
│   ├── views.py          # All views
│   ├── urls.py           # URL routes
│   └── admin.py
├── templates/
│   ├── base.html         # Sidebar layout + styles
│   └── workouts/         # Page templates
├── static/css/
├── manage.py
└── requirements.txt
```

## 🗄️ Models

### Exercise
- `name` - Exercise name
- `muscle_group` - chest, back, shoulders, legs, biceps, triceps, core

### Workout
- `date` - Workout date
- `day_type` - Workout type (Chest, Back, Push, Pull, etc.)
- `notes` - Optional notes

### Set
- `workout` - Foreign key to Workout
- `exercise` - Foreign key to Exercise
- `weight` - Weight in kg
- `reps` - Number of reps
- `notes` - Optional notes

## 💾 Backup

```bash
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3
```

---

**Happy lifting! 🏋️**
