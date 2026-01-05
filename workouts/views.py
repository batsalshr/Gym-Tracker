"""Views for gym workout tracking."""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Max, Count, Sum
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta

from .models import Exercise, Workout, Set


class DashboardView(View):
    """Main dashboard."""
    
    def get(self, request):
        # Recent workouts
        recent_workouts = Workout.objects.prefetch_related('sets__exercise')[:5]
        
        # Stats
        total_workouts = Workout.objects.count()
        
        # This week's workouts
        week_ago = timezone.now().date() - timedelta(days=7)
        this_week = Workout.objects.filter(date__gte=week_ago).count()
        
        # Weekly volume
        weekly_volume = 0
        for workout in Workout.objects.filter(date__gte=week_ago):
            weekly_volume += workout.get_total_volume()
        
        # Last workout info
        last_workout = Workout.objects.first()
        
        # Personal bests (top 4 by weight)
        personal_bests = []
        exercises_with_sets = Exercise.objects.annotate(
            max_weight=Max('sets__weight'),
            set_count=Count('sets')
        ).filter(set_count__gt=0).order_by('-max_weight')[:4]
        
        for ex in exercises_with_sets:
            pb = ex.get_personal_best()
            if pb:
                personal_bests.append({
                    'exercise': ex,
                    'weight': pb.weight,
                    'reps': pb.reps,
                    'date': pb.workout.date
                })
        
        # Muscle group stats (past 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_sets = Set.objects.filter(
            workout__date__gte=thirty_days_ago
        ).select_related('exercise')
        
        muscle_group_stats = {}
        for mg_code, mg_display in Exercise.MUSCLE_GROUPS:
            muscle_group_stats[mg_display] = {
                'code': mg_code,
                'volume': 0,
                'sets': 0,
                'exercises': set()
            }
        
        for s in recent_sets:
            mg_display = s.exercise.get_muscle_group_display()
            muscle_group_stats[mg_display]['volume'] += s.weight * s.reps
            muscle_group_stats[mg_display]['sets'] += 1
            muscle_group_stats[mg_display]['exercises'].add(s.exercise.name)
        
        # Convert exercise sets to lists for template
        for stats in muscle_group_stats.values():
            stats['exercise_count'] = len(stats['exercises'])
            stats['exercises'] = list(stats['exercises'])
        
        # Sort by volume (descending)
        muscle_group_stats = dict(sorted(
            muscle_group_stats.items(),
            key=lambda x: x[1]['volume'],
            reverse=True
        ))
        
        context = {
            'recent_workouts': recent_workouts,
            'total_workouts': total_workouts,
            'this_week': this_week,
            'weekly_volume': weekly_volume,
            'last_workout': last_workout,
            'personal_bests': personal_bests,
            'muscle_group_stats': muscle_group_stats,
        }
        return render(request, 'workouts/dashboard.html', context)


class LogWorkoutView(View):
    """Log a new workout - Step 1: Basic info."""
    
    def get(self, request):
        context = {
            'day_types': Workout.DAY_TYPES,
            'today': timezone.now().date().isoformat(),
        }
        return render(request, 'workouts/log_workout.html', context)
    
    def post(self, request):
        day_type = request.POST.get('day_type')
        date = request.POST.get('date') or timezone.now().date()
        notes = request.POST.get('notes', '')
        
        workout = Workout.objects.create(
            day_type=day_type,
            date=date,
            notes=notes
        )
        
        return redirect('add_exercises', workout_id=workout.id)


class AddExercisesView(View):
    """Log workout - Step 2: Add exercises and sets."""
    
    def get(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id)
        
        # Get exercises grouped by muscle group
        exercises_by_group = {}
        for exercise in Exercise.objects.all():
            group = exercise.get_muscle_group_display()
            if group not in exercises_by_group:
                exercises_by_group[group] = []
            exercises_by_group[group].append(exercise)
        
        # Get already logged sets grouped by exercise
        logged_exercises = workout.get_exercises_summary()
        
        context = {
            'workout': workout,
            'exercises_by_group': exercises_by_group,
            'logged_exercises': logged_exercises,
        }
        return render(request, 'workouts/add_exercises.html', context)
    
    def post(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id)
        
        exercise_id = request.POST.get('exercise')
        exercise = get_object_or_404(Exercise, id=exercise_id)
        
        # Get all weight/reps from form
        weights = request.POST.getlist('weight')
        reps_list = request.POST.getlist('reps')
        notes_list = request.POST.getlist('set_notes')
        
        sets_created = 0
        for i in range(len(weights)):
            if weights[i] and reps_list[i]:
                Set.objects.create(
                    workout=workout,
                    exercise=exercise,
                    set_number=i + 1,
                    weight=weights[i],
                    reps=reps_list[i],
                    notes=notes_list[i] if i < len(notes_list) else ''
                )
                sets_created += 1
        
        if sets_created > 0:
            messages.success(request, f'Added {sets_created} sets of {exercise.name}')
        
        # Check if user wants to finish
        if 'finish' in request.POST:
            return redirect('workout_detail', workout_id=workout.id)
        
        return redirect('add_exercises', workout_id=workout.id)


class WorkoutDetailView(View):
    """View workout details."""
    
    def get(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id)
        exercises_data = workout.get_exercises_summary()
        
        context = {
            'workout': workout,
            'exercises_data': exercises_data,
            'total_volume': workout.get_total_volume(),
        }
        return render(request, 'workouts/workout_detail.html', context)


class HistoryView(View):
    """Workout history."""
    
    def get(self, request):
        workouts = Workout.objects.prefetch_related('sets__exercise').all()
        
        context = {
            'workouts': workouts,
        }
        return render(request, 'workouts/history.html', context)


class DeleteWorkoutView(View):
    """Delete a workout."""
    
    def post(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id)
        workout.delete()
        messages.success(request, 'Workout deleted.')
        return redirect('history')


class DeleteSetView(View):
    """Delete a single set."""
    
    def post(self, request, set_id):
        set_obj = get_object_or_404(Set, id=set_id)
        workout_id = set_obj.workout.id
        set_obj.delete()
        messages.success(request, 'Set deleted.')
        return redirect('add_exercises', workout_id=workout_id)


class PersonalBestsView(View):
    """Personal bests page."""
    
    def get(self, request):
        sort_by = request.GET.get('sort', 'weight')
        
        personal_bests = []
        for exercise in Exercise.objects.annotate(set_count=Count('sets')).filter(set_count__gt=0):
            if sort_by == 'reps':
                pb = exercise.sets.order_by('-reps', '-weight').first()
            else:
                pb = exercise.get_personal_best()
            
            if pb:
                personal_bests.append({
                    'exercise': exercise,
                    'weight': pb.weight,
                    'reps': pb.reps,
                    'date': pb.workout.date,
                    'suggestion': exercise.get_suggested_weight()
                })
        
        if sort_by == 'reps':
            personal_bests.sort(key=lambda x: x['reps'], reverse=True)
        else:
            personal_bests.sort(key=lambda x: x['weight'], reverse=True)
        
        context = {
            'personal_bests': personal_bests,
            'sort_by': sort_by,
        }
        return render(request, 'workouts/personal_bests.html', context)


class ExerciseListView(View):
    """Manage exercises."""
    
    def get(self, request):
        exercises_by_group = {}
        for exercise in Exercise.objects.annotate(set_count=Count('sets')).all():
            group = exercise.get_muscle_group_display()
            if group not in exercises_by_group:
                exercises_by_group[group] = []
            exercises_by_group[group].append(exercise)
        
        context = {
            'exercises_by_group': exercises_by_group,
            'muscle_groups': Exercise.MUSCLE_GROUPS,
        }
        return render(request, 'workouts/exercises.html', context)
    
    def post(self, request):
        name = request.POST.get('name')
        muscle_group = request.POST.get('muscle_group')
        
        if name and muscle_group:
            Exercise.objects.get_or_create(name=name, muscle_group=muscle_group)
            messages.success(request, f'{name} added!')
        
        return redirect('exercises')


# API Views
class ExerciseSuggestionAPI(View):
    """Get weight suggestion for an exercise."""
    
    def get(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id)
        suggestion = exercise.get_suggested_weight()
        last = exercise.get_last_workout()
        
        data = {
            'suggestion': float(suggestion) if suggestion else None,
            'last_weight': float(last.weight) if last else None,
            'last_reps': last.reps if last else None,
            'last_date': last.workout.date.isoformat() if last else None,
        }
        return JsonResponse(data)
