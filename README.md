# 🏋️ Gym Tracker

A comprehensive Django-based workout tracking application with a beautiful, modern UI that supports dark mode.

## ✨ Features

### Core Features
- **Multi-select Muscle Groups**: Select multiple muscle groups per workout (e.g., Chest + Triceps)
- **336 Exercises**: Comprehensive exercise database across all muscle groups
- **Smart Autocomplete Search**: Type to search exercises with keyboard navigation
- **Progressive Overload Tracking**: Weight suggestions based on your last performance
- **Personal Bests**: Track your PRs with automatic detection

### New Features
- **🌙 Dark Mode**: Toggle between light and dark themes
- **📁 Workout Templates**: Save and reuse your favorite workout routines
- **⚖️ Body Weight Tracking**: Track your weight over time with charts
- **🎯 Goals**: Set and track strength goals with progress bars (with autocomplete!)
- **🔍 Advanced History Filters**: Filter by date, muscle group, sets, and volume

### Exercise Database (336 Exercises)
| Muscle Group | Count |
|--------------|-------|
| Chest | 38 |
| Back | 45 |
| Shoulders | 37 |
| Legs | 63 |
| Biceps | 28 |
| Triceps | 28 |
| Core | 29 |
| Cardio | 26 |
| Glutes | 18 |
| Forearms | 8 |
| Calves | 8 |
| Traps | 8 |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install django
```

### 2. Set Up Database

```bash
python manage.py migrate
```

### 3. Load Exercise Database (336 exercises)

```bash
python load_exercises.py
```

### 4. (Optional) Load Demo Data

```bash
python demo_data.py
```

### 5. Run Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## 📱 Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Overview with stats, goals, and recent workouts |
| Log Workout | `/log/` | Start a new workout |
| History | `/history/` | View all workouts with filters |
| Personal Bests | `/personal-bests/` | Your record lifts |
| Body Weight | `/bodyweight/` | Track your weight |
| Templates | `/templates/` | Manage workout templates |
| Goals | `/goals/` | Set and track goals |
| Exercises | `/exercises/` | Browse and add exercises |

## 🎨 Dark Mode

Click the theme toggle button in the sidebar (🌙/☀️) to switch between light and dark modes. Your preference is saved automatically.

## 📝 Workout Flow

1. **Select Muscle Groups**: Choose one or more muscle groups, or use a saved template
2. **Add Exercises**: Type to search exercises with autocomplete, get weight suggestions
3. **Log Sets**: Enter weight and reps for each set
4. **Finish**: View your workout summary

## 🎯 Goals

Create goals with autocomplete exercise search:
- **Lift Weight**: Hit a target weight on an exercise (e.g., "Bench 100kg")
- **Reps at Weight**: Hit target reps at a specific weight
- **Body Weight**: Reach a target body weight
- **Weekly Volume**: Hit a target weekly volume

## 🔧 Customization

### Adding Custom Exercises

1. Go to `/exercises/`
2. Fill in the "Add Custom Exercise" form
3. Select muscle group and equipment type

### Creating Workout Templates

1. Go to `/templates/`
2. Create a new template with name and muscle groups
3. Edit to add specific exercises with target sets/reps
4. Use the template from the Log Workout page

## 📁 Project Structure

```
gym_tracker/
├── gym_tracker/          # Django project settings
├── workouts/             # Main app
│   ├── models.py         # Data models
│   ├── views.py          # View logic
│   └── urls.py           # URL routing
├── templates/
│   ├── base.html         # Base template with dark mode
│   └── workouts/         # Page templates
├── load_exercises.py     # Exercise database loader (336 exercises)
├── demo_data.py          # Demo data generator
└── manage.py
```

## 🔄 Starting Fresh

To reset the database:

```bash
rm db.sqlite3
python manage.py migrate
python load_exercises.py
python demo_data.py  # Optional
```

## 💡 Tips

- **Quick Presets**: Use preset buttons on Log Workout page (Push, Pull, Legs, etc.)
- **Exercise Priority**: Search prioritizes exercises matching your selected muscle groups
- **Weight Suggestions**: Based on last workout (8+ reps = increase, <5 reps = decrease)
- **Auto-Update Goals**: Goals update automatically when you log relevant workouts
- **Keyboard Navigation**: Use arrow keys and Enter in autocomplete dropdowns

## 🎨 Theme Colors

### Light Mode
- Background: #F0F2F5
- Cards: #FFFFFF
- Accent: #3A86FF

### Dark Mode
- Background: #1A1A2E
- Cards: #16213E
- Accent: #4F9CFF

---