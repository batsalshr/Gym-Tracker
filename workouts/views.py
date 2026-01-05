"""Views for gym workout tracking."""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Max, Count, Sum
from django.utils import timezone
from django.contrib import messages

from .models import Exercise, Workout, WorkoutExercise, Set


class DashboardView(View):
    """Main dashboard with overview."""
    
    def get(self, request):
        # Recent workouts
        recent_workouts = Workout.objects.prefetch_related('sets__exercise')[:5]
        
        # Stats
        total_workouts = Workout.objects.count()
        total_sets = Set.objects.count()
        
        # This week's workouts
        from datetime import timedelta
        week_ago = timezone.now().date() - timedelta(days=7)
        this_week = Workout.objects.filter(date__gte=week_ago).count()
        
        # Personal bests (top 5 by weight)
        personal_bests = []
        exercises_with_sets = Exercise.objects.annotate(
            max_weight=Max('sets__weight'),
            set_count=Count('sets')
        ).filter(set_count__gt=0).order_by('-max_weight')[:5]
        
        for ex in exercises_with_sets:
            pb = ex.get_personal_best()
            if pb:
                personal_bests.append({
                    'exercise': ex,
                    'weight': pb.weight,
                    'reps': pb.reps,
                    'date': pb.workout.date
                })
        
        context = {
            'recent_workouts': recent_workouts,
            'total_workouts': total_workouts,
            'total_sets': total_sets,
            'this_week': this_week,
            'personal_bests': personal_bests,
        }
        return render(request, 'workouts/dashboard.html', context)


class NewWorkoutView(View):
    """Step 1: Create new workout - select day type and date."""
    
    def get(self, request):
        context = {
            'day_types': Workout.DAY_TYPES,
            'today': timezone.now().date().isoformat(),
        }
        return render(request, 'workouts/new_workout.html', context)
    
    def post(self, request):
        day_type = request.POST.get('day_type')
        date = request.POST.get('date') or timezone.now().date()
        notes = request.POST.get('notes', '')
        
        workout = Workout.objects.create(
            day_type=day_type,
            date=date,
            notes=notes
        )
        
        return redirect('add_exercise', workout_id=workout.id)


class AddExerciseView(View):
    """Step 2: Add exercise to workout with number of sets."""
    
    def get(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id)
        
        # Get exercises grouped by muscle group
        exercises_by_group = {}
        for exercise in Exercise.objects.all():
            group = exercise.get_muscle_group_display()
            if group not in exercises_by_group:
                exercises_by_group[group] = []
            exercises_by_group[group].append(exercise)
        
        # Get already added exercises
        added_exercises = workout.workout_exercises.select_related('exercise').all()
        
        context = {
            'workout': workout,
            'exercises_by_group': exercises_by_group,
            'added_exercises': added_exercises,
        }
        return render(request, 'workouts/add_exercise.html', context)
    
    def post(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id)
        
        exercise_id = request.POST.get('exercise')
        num_sets = int(request.POST.get('num_sets', 3))
        
        exercise = get_object_or_404(Exercise, id=exercise_id)
        
        # Get next order number
        max_order = workout.workout_exercises.aggregate(Max('order'))['order__max'] or 0
        
        workout_exercise = WorkoutExercise.objects.create(
            workout=workout,
            exercise=exercise,
            num_sets=num_sets,
            order=max_order + 1
        )
        
        # Redirect to enter sets for this exercise
        return redirect('enter_sets', workout_id=workout.id, exercise_id=exercise.id)


class EnterSetsView(View):
    """Step 3: Enter weight and reps for each set."""
    
    def get(self, request, workout_id, exercise_id):
        workout = get_object_or_404(Workout, id=workout_id)
        exercise = get_object_or_404(Exercise, id=exercise_id)
        workout_exercise = get_object_or_404(WorkoutExercise, workout=workout, exercise=exercise)
        
        # Get existing sets
        existing_sets = Set.objects.filter(workout=workout, exercise=exercise).order_by('set_number')
        
        # Get suggestion
        suggestion = exercise.get_suggested_weight()
        last_workout = exercise.get_last_workout()
        
        context = {
            'workout': workout,
            'exercise': exercise,
            'workout_exercise': workout_exercise,
            'num_sets': workout_exercise.num_sets,
            'existing_sets': existing_sets,
            'suggestion': suggestion,
            'last_workout': last_workout,
        }
        return render(request, 'workouts/enter_sets.html', context)
    
    def post(self, request, workout_id, exercise_id):
        workout = get_object_or_404(Workout, id=workout_id)
        exercise = get_object_or_404(Exercise, id=exercise_id)
        workout_exercise = get_object_or_404(WorkoutExercise, workout=workout, exercise=exercise)
        
        # Clear existing sets for this exercise in this workout
        Set.objects.filter(workout=workout, exercise=exercise).delete()
        
        # Save all sets
        for i in range(1, workout_exercise.num_sets + 1):
            weight = request.POST.get(f'weight_{i}')
            reps = request.POST.get(f'reps_{i}')
            notes = request.POST.get(f'notes_{i}', '')
            
            if weight and reps:
                Set.objects.create(
                    workout=workout,
                    exercise=exercise,
                    set_number=i,
                    weight=weight,
                    reps=reps,
                    notes=notes
                )
        
        messages.success(request, f'{exercise.name} sets saved!')
        
        # Check if user wants to add another exercise
        if 'add_another' in request.POST:
            return redirect('add_exercise', workout_id=workout.id)
        
        return redirect('workout_detail', workout_id=workout.id)


class WorkoutDetailView(View):
    """View workout details."""
    
    def get(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id)
        
        # Group sets by exercise
        exercises_data = []
        for we in workout.workout_exercises.select_related('exercise').all():
            sets = Set.objects.filter(workout=workout, exercise=we.exercise).order_by('set_number')
            exercises_data.append({
                'exercise': we.exercise,
                'planned_sets': we.num_sets,
                'sets': sets,
                'total_volume': sum(s.get_volume() for s in sets)
            })
        
        context = {
            'workout': workout,
            'exercises_data': exercises_data,
            'total_volume': workout.get_total_volume(),
        }
        return render(request, 'workouts/workout_detail.html', context)


class WorkoutListView(View):
    """List all workouts."""
    
    def get(self, request):
        workouts = Workout.objects.prefetch_related('sets__exercise').all()
        
        context = {
            'workouts': workouts,
        }
        return render(request, 'workouts/workout_list.html', context)


class DeleteWorkoutView(View):
    """Delete a workout."""
    
    def post(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id)
        workout.delete()
        messages.success(request, 'Workout deleted.')
        return redirect('dashboard')


class ExerciseListView(View):
    """List all exercises."""
    
    def get(self, request):
        exercises_by_group = {}
        for exercise in Exercise.objects.annotate(set_count=Count('sets')).all():
            group = exercise.get_muscle_group_display()
            if group not in exercises_by_group:
                exercises_by_group[group] = []
            
            pb = exercise.get_personal_best()
            exercises_by_group[group].append({
                'exercise': exercise,
                'set_count': exercise.set_count,
                'pb': pb
            })
        
        context = {
            'exercises_by_group': exercises_by_group,
        }
        return render(request, 'workouts/exercise_list.html', context)


class AddExerciseTypeView(View):
    """Add a new exercise type."""
    
    def get(self, request):
        context = {
            'muscle_groups': Exercise.MUSCLE_GROUPS,
        }
        return render(request, 'workouts/add_exercise_type.html', context)
    
    def post(self, request):
        name = request.POST.get('name')
        muscle_group = request.POST.get('muscle_group')
        
        Exercise.objects.create(name=name, muscle_group=muscle_group)
        messages.success(request, f'{name} added!')
        
        return redirect('exercise_list')


class PersonalBestsView(View):
    """View all personal bests."""
    
    def get(self, request):
        sort_by = request.GET.get('sort', 'weight')
        
        personal_bests = []
        for exercise in Exercise.objects.annotate(set_count=Count('sets')).filter(set_count__gt=0):
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