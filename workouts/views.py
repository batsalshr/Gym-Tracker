"""Views for gym workout tracking."""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Max, Count, Sum, Q
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
import json

from .models import (
    Exercise, Workout, Set, 
    BodyWeight, WorkoutTemplate, TemplateExercise, Goal
)


class DashboardView(View):
    """Main dashboard."""
    
    def get(self, request):
        # Recent workouts
        recent_workouts = Workout.objects.prefetch_related('sets__exercise')[:5]
        
        # Stats
        total_workouts = Workout.objects.count()
        total_sets = Set.objects.count()
        
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
        
        # Streak calculation
        streak = 0
        current_date = timezone.now().date()
        while True:
            if Workout.objects.filter(date=current_date).exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        # Active goals
        active_goals = Goal.objects.filter(status='active')[:3]
        
        # Latest body weight
        latest_weight = BodyWeight.objects.first()
        
        # Templates for quick start
        templates = WorkoutTemplate.objects.all()[:3]
        
        context = {
            'recent_workouts': recent_workouts,
            'total_workouts': total_workouts,
            'total_sets': total_sets,
            'this_week': this_week,
            'weekly_volume': weekly_volume,
            'last_workout': last_workout,
            'personal_bests': personal_bests,
            'streak': streak,
            'active_goals': active_goals,
            'latest_weight': latest_weight,
            'templates': templates,
        }
        return render(request, 'workouts/dashboard.html', context)


class LogWorkoutView(View):
    """Log a new workout - Step 1: Select muscle groups."""
    
    def get(self, request):
        muscle_groups = Exercise.MUSCLE_GROUPS
        templates = WorkoutTemplate.objects.all()
        context = {
            'muscle_groups': muscle_groups,
            'templates': templates,
            'today': timezone.now().date().isoformat(),
        }
        return render(request, 'workouts/log_workout.html', context)
    
    def post(self, request):
        # Check if using a template
        template_id = request.POST.get('template')
        if template_id:
            template = get_object_or_404(WorkoutTemplate, id=template_id)
            selected_groups = template.muscle_groups.split(',')
        else:
            selected_groups = request.POST.getlist('muscle_groups')
        
        date = request.POST.get('date') or timezone.now().date()
        notes = request.POST.get('notes', '')
        
        if not selected_groups:
            messages.error(request, 'Please select at least one muscle group.')
            return redirect('log_workout')
        
        workout = Workout.objects.create(
            muscle_groups=','.join(selected_groups),
            date=date,
            notes=notes
        )
        
        return redirect('add_exercises', workout_id=workout.id)


class AddExercisesView(View):
    """Log workout - Step 2: Add exercises and sets."""
    
    def get(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id)
        selected_groups = workout.get_muscle_groups_list()
        
        # Get already logged sets grouped by exercise
        logged_exercises = workout.get_exercises_summary()
        
        context = {
            'workout': workout,
            'logged_exercises': logged_exercises,
            'selected_groups': selected_groups,
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
            
            # Update any related goals
            for goal in Goal.objects.filter(exercise=exercise, status='active'):
                goal.update_progress()
        
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
    """Workout history with filters."""
    
    def get(self, request):
        workouts = Workout.objects.prefetch_related('sets__exercise').all()
        
        # Filters
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        muscle_filter = request.GET.get('muscle')
        min_sets = request.GET.get('min_sets')
        min_volume = request.GET.get('min_volume')
        sort_by = request.GET.get('sort', '-date')
        
        if date_from:
            workouts = workouts.filter(date__gte=date_from)
        if date_to:
            workouts = workouts.filter(date__lte=date_to)
        if muscle_filter:
            workouts = workouts.filter(muscle_groups__icontains=muscle_filter)
        
        # Convert to list for filtering by computed properties
        workouts_list = list(workouts)
        
        if min_sets:
            workouts_list = [w for w in workouts_list if w.get_total_sets() >= int(min_sets)]
        if min_volume:
            workouts_list = [w for w in workouts_list if w.get_total_volume() >= int(min_volume)]
        
        # Sorting
        if sort_by == 'sets':
            workouts_list.sort(key=lambda w: w.get_total_sets(), reverse=True)
        elif sort_by == 'volume':
            workouts_list.sort(key=lambda w: w.get_total_volume(), reverse=True)
        elif sort_by == 'date':
            workouts_list.sort(key=lambda w: w.date)
        # Default is -date (newest first), already sorted by queryset
        
        context = {
            'workouts': workouts_list,
            'muscle_groups': Exercise.MUSCLE_GROUPS,
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'muscle': muscle_filter,
                'min_sets': min_sets,
                'min_volume': min_volume,
                'sort': sort_by,
            }
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
        filter_group = request.GET.get('group', '')
        
        exercises = Exercise.objects.annotate(set_count=Count('sets')).filter(set_count__gt=0)
        
        if filter_group:
            exercises = exercises.filter(muscle_group=filter_group)
        
        personal_bests = []
        for exercise in exercises:
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
            'filter_group': filter_group,
            'muscle_groups': Exercise.MUSCLE_GROUPS,
        }
        return render(request, 'workouts/personal_bests.html', context)


class ExerciseListView(View):
    """Manage exercises."""
    
    def get(self, request):
        search = request.GET.get('search', '')
        
        exercises_by_group = {}
        queryset = Exercise.objects.annotate(set_count=Count('sets'))
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        for exercise in queryset:
            group = exercise.get_muscle_group_display()
            if group not in exercises_by_group:
                exercises_by_group[group] = []
            exercises_by_group[group].append(exercise)
        
        context = {
            'exercises_by_group': exercises_by_group,
            'muscle_groups': Exercise.MUSCLE_GROUPS,
            'search': search,
            'total_count': Exercise.objects.count(),
        }
        return render(request, 'workouts/exercises.html', context)
    
    def post(self, request):
        name = request.POST.get('name')
        muscle_group = request.POST.get('muscle_group')
        equipment = request.POST.get('equipment', '')
        
        if name and muscle_group:
            Exercise.objects.get_or_create(
                name=name, 
                muscle_group=muscle_group,
                defaults={'equipment': equipment}
            )
            messages.success(request, f'{name} added!')
        
        return redirect('exercises')


class DeleteExerciseView(View):
    """Delete an exercise."""
    
    def post(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id)
        name = exercise.name
        exercise.delete()
        messages.success(request, f'{name} deleted.')
        return redirect('exercises')


class ProgressView(View):
    """Track progress for a specific exercise."""
    
    def get(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id)
        
        # Get all sets for this exercise, grouped by workout date
        sets_by_date = {}
        for s in exercise.sets.select_related('workout').order_by('workout__date'):
            date = s.workout.date
            if date not in sets_by_date:
                sets_by_date[date] = {
                    'max_weight': s.weight,
                    'total_volume': 0,
                    'sets': []
                }
            sets_by_date[date]['sets'].append(s)
            sets_by_date[date]['total_volume'] += s.weight * s.reps
            if s.weight > sets_by_date[date]['max_weight']:
                sets_by_date[date]['max_weight'] = s.weight
        
        # Convert to list for chart
        progress_data = [
            {
                'date': date.isoformat(),
                'max_weight': float(data['max_weight']),
                'volume': float(data['total_volume']),
                'sets': len(data['sets'])
            }
            for date, data in sorted(sets_by_date.items())
        ]
        
        # Calculate total volume across all time
        total_volume = sum(d['volume'] for d in progress_data)
        
        context = {
            'exercise': exercise,
            'progress_data': progress_data,
            'pb': exercise.get_personal_best(),
            'suggestion': exercise.get_suggested_weight(),
            'total_volume': total_volume,
        }
        return render(request, 'workouts/progress.html', context)


# ============= BODY WEIGHT =============

class BodyWeightView(View):
    """Body weight tracking."""
    
    def get(self, request):
        weights = BodyWeight.objects.all()[:30]
        
        # Chart data
        chart_data = [
            {'date': w.date.isoformat(), 'weight': float(w.weight)}
            for w in reversed(list(weights))
        ]
        
        # Stats
        latest = weights.first() if weights else None
        
        if weights.count() >= 2:
            oldest_in_range = weights[min(len(weights)-1, 29)]
            change = float(latest.weight - oldest_in_range.weight) if latest else 0
        else:
            change = 0
        
        context = {
            'weights': weights,
            'chart_data': chart_data,
            'latest': latest,
            'change': change,
            'today': timezone.now().date().isoformat(),
        }
        return render(request, 'workouts/bodyweight.html', context)
    
    def post(self, request):
        date = request.POST.get('date') or timezone.now().date()
        weight = request.POST.get('weight')
        notes = request.POST.get('notes', '')
        
        if weight:
            BodyWeight.objects.update_or_create(
                date=date,
                defaults={'weight': weight, 'notes': notes}
            )
            messages.success(request, f'Weight recorded: {weight}kg')
            
            # Update body weight goals
            for goal in Goal.objects.filter(goal_type='bodyweight', status='active'):
                goal.update_progress()
        
        return redirect('bodyweight')


class DeleteBodyWeightView(View):
    """Delete a body weight entry."""
    
    def post(self, request, weight_id):
        weight = get_object_or_404(BodyWeight, id=weight_id)
        weight.delete()
        messages.success(request, 'Entry deleted.')
        return redirect('bodyweight')


# ============= TEMPLATES =============

class TemplatesView(View):
    """Workout templates."""
    
    def get(self, request):
        templates = WorkoutTemplate.objects.prefetch_related('exercises__exercise').all()
        
        context = {
            'templates': templates,
            'muscle_groups': Exercise.MUSCLE_GROUPS,
        }
        return render(request, 'workouts/templates.html', context)
    
    def post(self, request):
        name = request.POST.get('name')
        muscle_groups = request.POST.getlist('muscle_groups')
        
        if name and muscle_groups:
            template = WorkoutTemplate.objects.create(
                name=name,
                muscle_groups=','.join(muscle_groups)
            )
            messages.success(request, f'Template "{name}" created!')
            return redirect('template_edit', template_id=template.id)
        
        messages.error(request, 'Please provide a name and select muscle groups.')
        return redirect('templates')


class TemplateEditView(View):
    """Edit a workout template."""
    
    def get(self, request, template_id):
        template = get_object_or_404(WorkoutTemplate, id=template_id)
        selected_groups = [mg.strip() for mg in template.muscle_groups.split(',')]
        
        # Get exercises for selected groups
        exercises = Exercise.objects.filter(muscle_group__in=selected_groups)
        
        context = {
            'template': template,
            'exercises': exercises,
            'muscle_groups': Exercise.MUSCLE_GROUPS,
        }
        return render(request, 'workouts/template_edit.html', context)
    
    def post(self, request, template_id):
        template = get_object_or_404(WorkoutTemplate, id=template_id)
        
        exercise_id = request.POST.get('exercise')
        target_sets = request.POST.get('target_sets', 3)
        target_reps = request.POST.get('target_reps', '8-12')
        
        if exercise_id:
            exercise = get_object_or_404(Exercise, id=exercise_id)
            order = template.exercises.count()
            
            TemplateExercise.objects.create(
                template=template,
                exercise=exercise,
                order=order,
                target_sets=target_sets,
                target_reps=target_reps
            )
            messages.success(request, f'Added {exercise.name} to template.')
        
        return redirect('template_edit', template_id=template.id)


class DeleteTemplateView(View):
    """Delete a template."""
    
    def post(self, request, template_id):
        template = get_object_or_404(WorkoutTemplate, id=template_id)
        template.delete()
        messages.success(request, 'Template deleted.')
        return redirect('templates')


class DeleteTemplateExerciseView(View):
    """Remove exercise from template."""
    
    def post(self, request, exercise_id):
        te = get_object_or_404(TemplateExercise, id=exercise_id)
        template_id = te.template.id
        te.delete()
        messages.success(request, 'Exercise removed from template.')
        return redirect('template_edit', template_id=template_id)


class UseTemplateView(View):
    """Start a workout from a template."""
    
    def post(self, request, template_id):
        template = get_object_or_404(WorkoutTemplate, id=template_id)
        
        # Create workout
        workout = Workout.objects.create(
            muscle_groups=template.muscle_groups,
            date=timezone.now().date(),
            notes=f'From template: {template.name}'
        )
        
        messages.success(request, f'Started workout from "{template.name}"')
        return redirect('add_exercises', workout_id=workout.id)


# ============= GOALS =============

class GoalsView(View):
    """Goals page."""
    
    def get(self, request):
        active_goals = Goal.objects.filter(status='active')
        achieved_goals = Goal.objects.filter(status='achieved')[:10]
        
        exercises = Exercise.objects.all()
        
        context = {
            'active_goals': active_goals,
            'achieved_goals': achieved_goals,
            'exercises': exercises,
            'goal_types': Goal.GOAL_TYPES,
            'today': timezone.now().date(),
        }
        return render(request, 'workouts/goals.html', context)
    
    def post(self, request):
        name = request.POST.get('name')
        goal_type = request.POST.get('goal_type')
        exercise_id = request.POST.get('exercise')
        target_value = request.POST.get('target_value')
        target_reps = request.POST.get('target_reps')
        deadline = request.POST.get('deadline') or None
        
        if name and goal_type and target_value:
            goal = Goal.objects.create(
                name=name,
                goal_type=goal_type,
                exercise_id=exercise_id if exercise_id else None,
                target_value=target_value,
                target_reps=target_reps if target_reps else None,
                deadline=deadline
            )
            
            # Set initial current value
            goal.update_progress()
            
            messages.success(request, f'Goal "{name}" created!')
        
        return redirect('goals')


class UpdateGoalView(View):
    """Update goal progress."""
    
    def post(self, request, goal_id):
        goal = get_object_or_404(Goal, id=goal_id)
        goal.update_progress()
        messages.success(request, f'Goal "{goal.name}" updated!')
        return redirect('goals')


class DeleteGoalView(View):
    """Delete a goal."""
    
    def post(self, request, goal_id):
        goal = get_object_or_404(Goal, id=goal_id)
        goal.delete()
        messages.success(request, 'Goal deleted.')
        return redirect('goals')


# ============= API VIEWS =============

class ExerciseSuggestionAPI(View):
    """Get weight suggestion for an exercise."""
    
    def get(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id)
        suggestion = exercise.get_suggested_weight()
        last = exercise.get_last_workout()
        pb = exercise.get_personal_best()
        
        data = {
            'suggestion': float(suggestion) if suggestion else None,
            'last_weight': float(last.weight) if last else None,
            'last_reps': last.reps if last else None,
            'last_date': last.workout.date.isoformat() if last else None,
            'pb_weight': float(pb.weight) if pb else None,
            'pb_reps': pb.reps if pb else None,
        }
        return JsonResponse(data)


class ExerciseSearchAPI(View):
    """Search exercises for autocomplete."""
    
    def get(self, request):
        query = request.GET.get('q', '')
        muscle_groups = request.GET.get('groups', '').split(',')
        limit = int(request.GET.get('limit', 20))
        
        exercises = Exercise.objects.all()
        
        if query:
            exercises = exercises.filter(name__icontains=query)
        
        if muscle_groups and muscle_groups[0]:
            # Prioritize exercises from selected muscle groups
            in_group = exercises.filter(muscle_group__in=muscle_groups)[:limit]
            other = exercises.exclude(muscle_group__in=muscle_groups)[:max(0, limit - in_group.count())]
            
            results = list(in_group) + list(other)
        else:
            results = list(exercises[:limit])
        
        data = [
            {
                'id': e.id,
                'name': e.name,
                'muscle_group': e.muscle_group,
                'muscle_group_display': e.get_muscle_group_display(),
                'equipment': e.equipment,
            }
            for e in results
        ]
        
        return JsonResponse({'results': data})
