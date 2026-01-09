"""Views for gym workout tracking."""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Max, Count, Sum, Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
import json

from .models import (
    Exercise, Workout, Set, 
    BodyWeight, WorkoutTemplate, TemplateExercise, Goal,
    BodyMeasurement, Achievement
)


class DashboardView(LoginRequiredMixin, View):
    """Main dashboard."""
    
    def get(self, request):
        user = request.user
        
        # Recent workouts (user's only)
        recent_workouts = Workout.objects.filter(user=user).prefetch_related('sets__exercise')[:5]
        
        # Stats
        total_workouts = Workout.objects.filter(user=user).count()
        total_sets = Set.objects.filter(workout__user=user).count()
        
        # This week's workouts
        week_ago = timezone.now().date() - timedelta(days=7)
        this_week = Workout.objects.filter(user=user, date__gte=week_ago).count()
        
        # Weekly volume
        weekly_volume = 0
        for workout in Workout.objects.filter(user=user, date__gte=week_ago):
            weekly_volume += workout.get_total_volume()
        
        # Last workout info
        last_workout = Workout.objects.filter(user=user).first()
        
        # Personal bests (top 4 by weight)
        personal_bests = []
        exercises_with_sets = Exercise.objects.filter(
            Q(user=user) | Q(user__isnull=True)
        ).annotate(
            max_weight=Max('sets__weight', filter=Q(sets__workout__user=user)),
            set_count=Count('sets', filter=Q(sets__workout__user=user))
        ).filter(set_count__gt=0).order_by('-max_weight')[:4]
        
        for ex in exercises_with_sets:
            pb = ex.get_personal_best(user)
            if pb:
                personal_bests.append({
                    'exercise': ex,
                    'weight': pb.weight,
                    'reps': pb.reps,
                    'date': pb.workout.date
                })
        
        # Streak calculation - check from today or yesterday
        streak = 0
        current_date = timezone.now().date()
        
        # If no workout today, start checking from yesterday
        if not Workout.objects.filter(user=user, date=current_date).exists():
            current_date -= timedelta(days=1)
        
        # Count consecutive days with workouts
        while Workout.objects.filter(user=user, date=current_date).exists():
            streak += 1
            current_date -= timedelta(days=1)
        
        # Active goals
        active_goals = Goal.objects.filter(user=user, status='active')[:3]
        
        # Latest body weight
        latest_weight = BodyWeight.objects.filter(user=user).first()
        
        # Templates for quick start
        templates = WorkoutTemplate.objects.filter(Q(user=user) | Q(user__isnull=True))[:3]
        
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


class LogWorkoutView(LoginRequiredMixin, View):
    """Log a new workout - Step 1: Select muscle groups."""
    
    def get(self, request):
        muscle_groups = Exercise.MUSCLE_GROUPS
        templates = WorkoutTemplate.objects.filter(
            Q(user=request.user) | Q(user__isnull=True)
        )
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
            user=request.user,
            muscle_groups=','.join(selected_groups),
            date=date,
            notes=notes
        )
        
        return redirect('add_exercises', workout_id=workout.id)


class AddExercisesView(LoginRequiredMixin, View):
    """Log workout - Step 2: Add exercises and sets."""
    
    def get(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id, user=request.user)
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


class WorkoutDetailView(LoginRequiredMixin, View):
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


class HistoryView(LoginRequiredMixin, View):
    """Workout history with filters."""
    
    def get(self, request):
        user = request.user
        workouts = Workout.objects.filter(user=user).prefetch_related('sets__exercise')
        
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


class DeleteWorkoutView(LoginRequiredMixin, View):
    """Delete a workout."""
    
    def post(self, request, workout_id):
        workout = get_object_or_404(Workout, id=workout_id, user=request.user)
        workout.delete()
        messages.success(request, 'Workout deleted.')
        return redirect('history')


class DeleteSetView(LoginRequiredMixin, View):
    """Delete a single set."""
    
    def post(self, request, set_id):
        set_obj = get_object_or_404(Set, id=set_id)
        workout_id = set_obj.workout.id
        set_obj.delete()
        messages.success(request, 'Set deleted.')
        return redirect('add_exercises', workout_id=workout_id)


class PersonalBestsView(LoginRequiredMixin, View):
    """Personal bests page."""
    
    def get(self, request):
        user = request.user
        sort_by = request.GET.get('sort', 'weight')
        filter_group = request.GET.get('group', '')
        
        # Get exercises that have sets logged by this user
        exercises = Exercise.objects.filter(
            Q(user=user) | Q(user__isnull=True)
        ).annotate(
            set_count=Count('sets', filter=Q(sets__workout__user=user))
        ).filter(set_count__gt=0)
        
        if filter_group:
            exercises = exercises.filter(muscle_group=filter_group)
        
        personal_bests = []
        for exercise in exercises:
            if sort_by == 'reps':
                pb = exercise.sets.filter(workout__user=user).order_by('-reps', '-weight').first()
            else:
                pb = exercise.get_personal_best(user)
            
            if pb:
                personal_bests.append({
                    'exercise': exercise,
                    'weight': pb.weight,
                    'reps': pb.reps,
                    'date': pb.workout.date,
                    'suggestion': exercise.get_suggested_weight(user)
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


class ExerciseListView(LoginRequiredMixin, View):
    """Manage exercises."""
    
    def get(self, request):
        search = request.GET.get('search', '')
        
        # Muscle group Font Awesome icons
        MUSCLE_ICONS = {
            'chest': 'fa-heart-pulse',
            'back': 'fa-arrows-up-down',
            'shoulders': 'fa-child-reaching',
            'legs': 'fa-person-walking',
            'biceps': 'fa-dumbbell',
            'triceps': 'fa-hand-fist',
            'core': 'fa-circle-dot',
            'cardio': 'fa-heart',
            'glutes': 'fa-hippo',
            'forearms': 'fa-hand',
            'calves': 'fa-socks',
            'traps': 'fa-diamond'
        }
        
        selected_group = request.GET.get('group')
        search = request.GET.get('search', '')
        
        if selected_group:
            # Show exercises for specific muscle group
            queryset = Exercise.objects.filter(
                Q(user=request.user) | Q(user__isnull=True),
                muscle_group=selected_group
            ).annotate(
                set_count=Count('sets', filter=Q(sets__workout__user=request.user))
            ).order_by('name')
            
            if search:
                queryset = queryset.filter(name__icontains=search)
            
            selected_group_display = dict(Exercise.MUSCLE_GROUPS).get(selected_group, selected_group)
            
            context = {
                'selected_group': selected_group,
                'selected_group_display': selected_group_display,
                'group_icon': MUSCLE_ICONS.get(selected_group, 'fa-dumbbell'),
                'exercises': queryset,
                'search': search,
                'muscle_groups': Exercise.MUSCLE_GROUPS,
            }
        else:
            # Show muscle group cards
            muscle_group_data = []
            for value, label in Exercise.MUSCLE_GROUPS:
                count = Exercise.objects.filter(
                    Q(user=request.user) | Q(user__isnull=True),
                    muscle_group=value
                ).count()
                muscle_group_data.append({
                    'value': value,
                    'label': label,
                    'icon': MUSCLE_ICONS.get(value, 'fa-dumbbell'),
                    'count': count,
                })
            
            context = {
                'selected_group': None,
                'muscle_group_data': muscle_group_data,
                'muscle_groups': Exercise.MUSCLE_GROUPS,
                'total_count': Exercise.objects.filter(
                    Q(user=request.user) | Q(user__isnull=True)
                ).count(),
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
        
        # Redirect back to the muscle group page if we were on one
        if muscle_group:
            return redirect(f'/exercises/?group={muscle_group}')
        return redirect('exercises')


class DeleteExerciseView(LoginRequiredMixin, View):
    """Delete an exercise."""
    
    def post(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id)
        name = exercise.name
        exercise.delete()
        messages.success(request, f'{name} deleted.')
        return redirect('exercises')


class ProgressView(LoginRequiredMixin, View):
    """Comprehensive exercise detail page."""
    
    def get(self, request, exercise_id):
        from datetime import timedelta
        from decimal import Decimal
        
        user = request.user
        exercise = get_object_or_404(Exercise, id=exercise_id)
        
        # Get all sets for this exercise by this user
        all_sets = list(exercise.sets.filter(workout__user=user).select_related('workout').order_by('-workout__date', '-id'))
        
        # Group by workout date
        sets_by_date = {}
        for s in all_sets:
            date = s.workout.date
            if date not in sets_by_date:
                sets_by_date[date] = {
                    'max_weight': s.weight,
                    'max_reps': s.reps,
                    'total_volume': Decimal('0'),
                    'sets': [],
                    'date': date
                }
            sets_by_date[date]['sets'].append(s)
            sets_by_date[date]['total_volume'] += s.weight * s.reps
            if s.weight > sets_by_date[date]['max_weight']:
                sets_by_date[date]['max_weight'] = s.weight
                sets_by_date[date]['max_reps'] = s.reps
        
        # Progress data for chart (sorted by date ascending)
        progress_data = [
            {
                'date': data['date'].strftime('%b %d'),
                'max_weight': float(data['max_weight']),
                'volume': float(data['total_volume']),
                'sets': len(data['sets'])
            }
            for date, data in sorted(sets_by_date.items())
        ]
        
        # History data (sorted by date descending, limit 10)
        history = [
            {
                'date': data['date'],
                'sets': len(data['sets']),
                'max_weight': data['max_weight'],
                'max_reps': data['max_reps'],
                'volume': data['total_volume']
            }
            for date, data in sorted(sets_by_date.items(), reverse=True)[:10]
        ]
        
        # Best sets (by estimated 1RM)
        best_sets = []
        for s in all_sets:
            # Brzycki formula for estimated 1RM
            if s.reps > 0 and s.reps <= 12:
                estimated_1rm = float(s.weight) * (36 / (37 - s.reps))
            else:
                estimated_1rm = float(s.weight)
            s.estimated_1rm = estimated_1rm
            best_sets.append(s)
        
        best_sets = sorted(best_sets, key=lambda x: x.estimated_1rm, reverse=True)[:5]
        
        # Calculate analytics
        total_volume = sum(d['volume'] for d in progress_data)
        total_sessions = len(sets_by_date)
        total_sets = len(all_sets)
        
        avg_weight = sum(float(s.weight) for s in all_sets) / len(all_sets) if all_sets else 0
        avg_reps = sum(s.reps for s in all_sets) / len(all_sets) if all_sets else 0
        avg_sets = total_sets / total_sessions if total_sessions else 0
        
        # Frequency (times per month, based on last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_sessions = sum(1 for date in sets_by_date.keys() if date >= thirty_days_ago)
        frequency = recent_sessions
        
        # Weight progress (% change in last 30 days)
        weight_progress = 0
        recent_data = [d for d in progress_data if d['date']]
        if len(recent_data) >= 2:
            first_weight = recent_data[0]['max_weight']
            last_weight = recent_data[-1]['max_weight']
            if first_weight > 0:
                weight_progress = ((last_weight - first_weight) / first_weight) * 100
        
        # Muscle activation data
        MUSCLE_ACTIVATION = {
            'chest': [
                {'name': 'Chest (Pectorals)', 'level': 'primary'},
                {'name': 'Front Deltoids', 'level': 'secondary'},
                {'name': 'Triceps', 'level': 'secondary'},
                {'name': 'Core', 'level': 'tertiary'},
            ],
            'back': [
                {'name': 'Latissimus Dorsi', 'level': 'primary'},
                {'name': 'Rhomboids', 'level': 'primary'},
                {'name': 'Biceps', 'level': 'secondary'},
                {'name': 'Rear Deltoids', 'level': 'secondary'},
                {'name': 'Forearms', 'level': 'tertiary'},
            ],
            'shoulders': [
                {'name': 'Deltoids', 'level': 'primary'},
                {'name': 'Trapezius', 'level': 'secondary'},
                {'name': 'Triceps', 'level': 'secondary'},
                {'name': 'Core', 'level': 'tertiary'},
            ],
            'legs': [
                {'name': 'Quadriceps', 'level': 'primary'},
                {'name': 'Hamstrings', 'level': 'primary'},
                {'name': 'Glutes', 'level': 'secondary'},
                {'name': 'Calves', 'level': 'tertiary'},
                {'name': 'Core', 'level': 'tertiary'},
            ],
            'biceps': [
                {'name': 'Biceps Brachii', 'level': 'primary'},
                {'name': 'Brachialis', 'level': 'primary'},
                {'name': 'Forearms', 'level': 'secondary'},
            ],
            'triceps': [
                {'name': 'Triceps Brachii', 'level': 'primary'},
                {'name': 'Shoulders', 'level': 'secondary'},
                {'name': 'Chest', 'level': 'tertiary'},
            ],
            'core': [
                {'name': 'Rectus Abdominis', 'level': 'primary'},
                {'name': 'Obliques', 'level': 'primary'},
                {'name': 'Transverse Abdominis', 'level': 'secondary'},
                {'name': 'Lower Back', 'level': 'tertiary'},
            ],
            'glutes': [
                {'name': 'Gluteus Maximus', 'level': 'primary'},
                {'name': 'Gluteus Medius', 'level': 'secondary'},
                {'name': 'Hamstrings', 'level': 'secondary'},
                {'name': 'Core', 'level': 'tertiary'},
            ],
            'calves': [
                {'name': 'Gastrocnemius', 'level': 'primary'},
                {'name': 'Soleus', 'level': 'primary'},
            ],
            'traps': [
                {'name': 'Trapezius', 'level': 'primary'},
                {'name': 'Rhomboids', 'level': 'secondary'},
                {'name': 'Rear Deltoids', 'level': 'secondary'},
            ],
            'forearms': [
                {'name': 'Forearm Flexors', 'level': 'primary'},
                {'name': 'Forearm Extensors', 'level': 'primary'},
                {'name': 'Grip', 'level': 'secondary'},
            ],
        }
        
        muscles_worked = MUSCLE_ACTIVATION.get(exercise.muscle_group, [])
        
        # Determine movement type
        MOVEMENT_TYPES = {
            'chest': 'Push (Horizontal)',
            'back': 'Pull',
            'shoulders': 'Push (Vertical)',
            'legs': 'Compound',
            'biceps': 'Pull (Isolation)',
            'triceps': 'Push (Isolation)',
            'core': 'Stability',
            'glutes': 'Hip Hinge',
            'calves': 'Isolation',
            'traps': 'Pull',
            'forearms': 'Isolation',
        }
        movement_type = MOVEMENT_TYPES.get(exercise.muscle_group, 'Compound')
        
        # Effectiveness score (based on compound movements being more effective)
        EFFECTIVENESS = {
            'chest': 85, 'back': 90, 'shoulders': 80, 'legs': 95,
            'biceps': 70, 'triceps': 70, 'core': 75, 'glutes': 88,
            'calves': 60, 'traps': 72, 'forearms': 55,
        }
        effectiveness = EFFECTIVENESS.get(exercise.muscle_group, 70)
        
        context = {
            'exercise': exercise,
            'progress_data': progress_data,
            'history': history,
            'best_sets': best_sets,
            'pb': exercise.get_personal_best(user),
            'suggestion': exercise.get_suggested_weight(user),
            'total_volume': total_volume,
            'total_sessions': total_sessions,
            'avg_weight': avg_weight,
            'avg_reps': avg_reps,
            'avg_sets': avg_sets,
            'frequency': frequency,
            'weight_progress': weight_progress,
            'muscles_worked': muscles_worked,
            'movement_type': movement_type,
            'effectiveness': effectiveness,
        }
        return render(request, 'workouts/exercise_detail.html', context)


# ============= BODY WEIGHT =============

class BodyWeightView(LoginRequiredMixin, View):
    """Body weight tracking."""
    
    def get(self, request):
        user = request.user
        weights = BodyWeight.objects.filter(user=user)[:30]
        
        # Chart data
        chart_data = [
            {'date': w.date.strftime('%b %d'), 'weight': float(w.weight)}
            for w in reversed(list(weights))
        ]
        
        # Stats
        latest = weights.first() if weights else None
        total_entries = BodyWeight.objects.filter(user=user).count()
        
        weight_change = 0
        if weights.count() >= 2:
            oldest_in_range = weights[min(len(weights)-1, 29)]
            weight_change = float(latest.weight - oldest_in_range.weight) if latest else 0
        
        context = {
            'weights': weights,
            'chart_data': chart_data,
            'latest': latest,
            'weight_change': weight_change,
            'total_entries': total_entries,
            'today': timezone.now().date(),
        }
        return render(request, 'workouts/bodyweight.html', context)
    
    def post(self, request):
        user = request.user
        date = request.POST.get('date') or timezone.now().date()
        weight = request.POST.get('weight')
        notes = request.POST.get('notes', '')
        
        if weight:
            BodyWeight.objects.update_or_create(
                user=user,
                date=date,
                defaults={'weight': weight, 'notes': notes}
            )
            messages.success(request, f'Weight recorded: {weight}kg')
            
            # Update body weight goals for this user
            for goal in Goal.objects.filter(user=user, goal_type='bodyweight', status='active'):
                goal.update_progress()
        
        return redirect('bodyweight')


class DeleteBodyWeightView(LoginRequiredMixin, View):
    """Delete a body weight entry."""
    
    def post(self, request, weight_id):
        weight = get_object_or_404(BodyWeight, id=weight_id, user=request.user)
        weight.delete()
        messages.success(request, 'Entry deleted.')
        return redirect('bodyweight')


# ============= TEMPLATES =============

class TemplatesView(LoginRequiredMixin, View):
    """Workout templates."""
    
    def get(self, request):
        user = request.user
        templates = WorkoutTemplate.objects.filter(
            Q(user=user) | Q(user__isnull=True)
        ).prefetch_related('exercises__exercise')
        
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
                muscle_groups=','.join(muscle_groups),
                user=request.user
            )
            messages.success(request, f'Template "{name}" created!')
            return redirect('template_edit', template_id=template.id)
        
        messages.error(request, 'Please provide a name and select muscle groups.')
        return redirect('templates')


class TemplateEditView(LoginRequiredMixin, View):
    """Edit a workout template."""
    
    def get(self, request, template_id):
        template = get_object_or_404(WorkoutTemplate, id=template_id)
        # Check ownership (allow if user owns it or it's a shared template)
        if template.user and template.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('templates')
        
        selected_groups = [mg.strip() for mg in template.muscle_groups.split(',')]
        
        # Get exercises for selected groups
        exercises = Exercise.objects.filter(
            Q(user=request.user) | Q(user__isnull=True),
            muscle_group__in=selected_groups
        )
        
        context = {
            'template': template,
            'exercises': exercises,
            'muscle_groups': Exercise.MUSCLE_GROUPS,
        }
        return render(request, 'workouts/template_edit.html', context)
    
    def post(self, request, template_id):
        template = get_object_or_404(WorkoutTemplate, id=template_id)
        if template.user and template.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('templates')
        
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


class DeleteTemplateView(LoginRequiredMixin, View):
    """Delete a template."""
    
    def post(self, request, template_id):
        template = get_object_or_404(WorkoutTemplate, id=template_id)
        template.delete()
        messages.success(request, 'Template deleted.')
        return redirect('templates')


class DeleteTemplateExerciseView(LoginRequiredMixin, View):
    """Remove exercise from template."""
    
    def post(self, request, exercise_id):
        te = get_object_or_404(TemplateExercise, id=exercise_id)
        template_id = te.template.id
        te.delete()
        messages.success(request, 'Exercise removed from template.')
        return redirect('template_edit', template_id=template_id)


class UseTemplateView(LoginRequiredMixin, View):
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

class GoalsView(LoginRequiredMixin, View):
    """Goals page."""
    
    def get(self, request):
        user = request.user
        active_goals = Goal.objects.filter(user=user, status='active')
        achieved_goals = Goal.objects.filter(user=user, status='achieved')[:10]
        
        exercises = Exercise.objects.filter(Q(user=user) | Q(user__isnull=True))
        
        context = {
            'active_goals': active_goals,
            'achieved_goals': achieved_goals,
            'exercises': exercises,
            'goal_types': Goal.GOAL_TYPES,
            'today': timezone.now().date(),
        }
        return render(request, 'workouts/goals.html', context)
    
    def post(self, request):
        from decimal import Decimal, InvalidOperation
        
        user = request.user
        name = request.POST.get('name')
        goal_type = request.POST.get('goal_type')
        exercise_id = request.POST.get('exercise')
        target_value_str = request.POST.get('target_value')
        target_reps = request.POST.get('target_reps')
        deadline = request.POST.get('deadline') or None
        
        if name and goal_type and target_value_str:
            try:
                target_value = Decimal(target_value_str)
            except (InvalidOperation, ValueError):
                messages.error(request, 'Invalid target value')
                return redirect('goals')
            
            goal = Goal.objects.create(
                user=user,
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


class UpdateGoalView(LoginRequiredMixin, View):
    """Update goal progress."""
    
    def post(self, request, goal_id):
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        goal.update_progress()
        messages.success(request, f'Goal "{goal.name}" updated!')
        return redirect('goals')


class DeleteGoalView(LoginRequiredMixin, View):
    """Delete a goal."""
    
    def post(self, request, goal_id):
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        goal.delete()
        messages.success(request, 'Goal deleted.')
        return redirect('goals')


# ============= API VIEWS =============

class ExerciseSuggestionAPI(LoginRequiredMixin, View):
    """Get weight suggestion for an exercise."""
    
    def get(self, request, exercise_id):
        user = request.user
        exercise = get_object_or_404(Exercise, id=exercise_id)
        suggestion = exercise.get_suggested_weight(user)
        last = exercise.get_last_workout(user)
        pb = exercise.get_personal_best(user)
        
        data = {
            'suggestion': float(suggestion) if suggestion else None,
            'last_weight': float(last.weight) if last else None,
            'last_reps': last.reps if last else None,
            'last_date': last.workout.date.isoformat() if last else None,
            'pb_weight': float(pb.weight) if pb else None,
            'pb_reps': pb.reps if pb else None,
        }
        return JsonResponse(data)


class ExerciseSearchAPI(LoginRequiredMixin, View):
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


# ============= 1RM CALCULATOR =============

class CalculatorView(LoginRequiredMixin, View):
    """1RM Calculator page."""
    
    def get(self, request):
        return render(request, 'workouts/calculator.html')


# ============= BODY MEASUREMENTS =============

class MeasurementsView(LoginRequiredMixin, View):
    """Body measurements tracking."""
    
    def get(self, request):
        user = request.user
        measurements = BodyMeasurement.objects.filter(user=user)[:20]
        latest = measurements.first() if measurements else None
        
        # Get previous for comparison
        previous = measurements[1] if len(measurements) > 1 else None
        
        # Chart data for each measurement type
        chart_fields = ['chest', 'waist', 'left_arm', 'right_arm', 'left_thigh', 'right_thigh']
        chart_data = {}
        
        for field in chart_fields:
            data = []
            for m in reversed(list(measurements[:12])):
                val = getattr(m, field)
                if val:
                    data.append({'date': m.date.strftime('%b %d'), 'value': float(val)})
            if data:
                chart_data[field] = data
        
        context = {
            'measurements': measurements,
            'latest': latest,
            'previous': previous,
            'chart_data': chart_data,
            'today': timezone.now().date(),
        }
        return render(request, 'workouts/measurements.html', context)
    
    def post(self, request):
        user = request.user
        date = request.POST.get('date') or timezone.now().date()
        
        # Get or create measurement for date and user
        measurement, created = BodyMeasurement.objects.get_or_create(
            user=user, 
            date=date
        )
        
        fields = ['chest', 'waist', 'hips', 'left_arm', 'right_arm', 
                  'left_thigh', 'right_thigh', 'left_calf', 'right_calf',
                  'shoulders', 'neck', 'body_fat_percent']
        
        for field in fields:
            value = request.POST.get(field)
            if value:
                setattr(measurement, field, value)
        
        measurement.notes = request.POST.get('notes', '')
        measurement.save()
        
        # Check achievement
        if BodyMeasurement.objects.filter(user=user).count() == 1:
            Achievement.check_and_unlock(user, 'first_measurement')
        
        messages.success(request, 'Measurements saved!')
        return redirect('measurements')


class DeleteMeasurementView(LoginRequiredMixin, View):
    """Delete a measurement entry."""
    
    def post(self, request, measurement_id):
        measurement = get_object_or_404(BodyMeasurement, id=measurement_id, user=request.user)
        measurement.delete()
        messages.success(request, 'Measurement deleted.')
        return redirect('measurements')


# ============= CALENDAR =============

class CalendarView(LoginRequiredMixin, View):
    """Workout calendar view."""
    
    def get(self, request):
        # Get month/year from query params or use current
        import calendar
        from datetime import date
        
        user = request.user
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
        
        # Get workouts for this month (user's only)
        workouts = Workout.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        )
        
        # Create workout lookup by date
        workout_dates = {}
        for w in workouts:
            workout_dates[w.date.day] = {
                'id': w.id,
                'muscles': w.get_muscle_groups_display(),
                'sets': w.get_total_sets(),
                'volume': w.get_total_volume(),
            }
        
        # Calendar data
        cal = calendar.Calendar(firstweekday=0)  # Monday start
        weeks = cal.monthdayscalendar(year, month)
        
        # Navigation
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        
        context = {
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'weeks': weeks,
            'workout_dates': workout_dates,
            'today': timezone.now().date(),
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'total_workouts': workouts.count(),
            'total_volume': sum(w.get_total_volume() for w in workouts),
        }
        return render(request, 'workouts/calendar.html', context)


# ============= CHARTS DASHBOARD =============

class ChartsView(LoginRequiredMixin, View):
    """Charts and analytics dashboard."""
    
    def get(self, request):
        from datetime import timedelta
        from collections import defaultdict
        
        user = request.user
        today = timezone.now().date()
        
        # Volume over last 12 weeks
        volume_data = []
        for i in range(11, -1, -1):
            week_start = today - timedelta(days=today.weekday() + (i * 7))
            week_end = week_start + timedelta(days=6)
            
            workouts = Workout.objects.filter(user=user, date__gte=week_start, date__lte=week_end)
            total_volume = sum(w.get_total_volume() for w in workouts)
            
            volume_data.append({
                'week': week_start.strftime('%b %d'),
                'volume': float(total_volume),
            })
        
        # Workouts per week
        workout_count_data = []
        for i in range(11, -1, -1):
            week_start = today - timedelta(days=today.weekday() + (i * 7))
            week_end = week_start + timedelta(days=6)
            
            count = Workout.objects.filter(user=user, date__gte=week_start, date__lte=week_end).count()
            workout_count_data.append({
                'week': week_start.strftime('%b %d'),
                'count': count,
            })
        
        # Muscle group distribution (last 30 days)
        muscle_distribution = defaultdict(int)
        recent_workouts = Workout.objects.filter(user=user, date__gte=today - timedelta(days=30))
        
        for workout in recent_workouts:
            for mg in workout.get_muscle_groups_list():
                muscle_distribution[mg] += 1
        
        muscle_data = [
            {'muscle': dict(Exercise.MUSCLE_GROUPS).get(k, k), 'count': v}
            for k, v in sorted(muscle_distribution.items(), key=lambda x: -x[1])
        ]
        
        # PR Timeline (last 10 PRs)
        pr_data = []
        exercises_with_sets = Exercise.objects.filter(sets__workout__user=user).distinct()
        
        for exercise in exercises_with_sets:
            pb = exercise.get_personal_best(user)
            if pb:
                pr_data.append({
                    'exercise': exercise.name,
                    'weight': float(pb.weight),
                    'reps': pb.reps,
                    'date': pb.workout.date.strftime('%b %d'),
                })
        
        pr_data = sorted(pr_data, key=lambda x: x['weight'], reverse=True)[:10]
        
        # Body weight trend
        bodyweight_data = [
            {'date': bw.date.strftime('%b %d'), 'weight': float(bw.weight)}
            for bw in reversed(list(BodyWeight.objects.filter(user=user)[:30]))
        ]
        
        # Stats summary
        total_workouts = Workout.objects.filter(user=user).count()
        total_volume = sum(w.get_total_volume() for w in Workout.objects.filter(user=user))
        total_sets = Set.objects.filter(workout__user=user).count()
        
        context = {
            'volume_data': volume_data,
            'workout_count_data': workout_count_data,
            'muscle_data': muscle_data,
            'pr_data': pr_data,
            'bodyweight_data': bodyweight_data,
            'total_workouts': total_workouts,
            'total_volume': total_volume,
            'total_sets': total_sets,
        }
        return render(request, 'workouts/charts.html', context)


# ============= ACHIEVEMENTS =============

class AchievementsView(LoginRequiredMixin, View):
    """Achievements page."""
    
    def get(self, request):
        user = request.user
        
        # Check all achievements for this user
        self.check_all_achievements(user)
        
        # Get all possible achievements
        all_types = dict(Achievement.ACHIEVEMENT_TYPES)
        existing_types = set(Achievement.objects.filter(user=user).values_list('achievement_type', flat=True))
        
        # Create missing achievements for this user
        for atype in all_types.keys():
            if atype not in existing_types:
                Achievement.objects.create(user=user, achievement_type=atype, unlocked=False)
        
        unlocked = Achievement.objects.filter(user=user, unlocked=True).order_by('-unlocked_at')
        locked = Achievement.objects.filter(user=user, unlocked=False)
        
        context = {
            'unlocked': unlocked,
            'locked': locked,
            'total_unlocked': unlocked.count(),
            'total_achievements': len(all_types),
        }
        return render(request, 'workouts/achievements.html', context)
    
    def check_all_achievements(self, user):
        """Check and unlock all earned achievements for user."""
        from datetime import timedelta
        
        workout_count = Workout.objects.filter(user=user).count()
        total_volume = sum(w.get_total_volume() for w in Workout.objects.filter(user=user))
        
        # Workout milestones
        if workout_count >= 1:
            Achievement.check_and_unlock(user, 'first_workout')
        if workout_count >= 10:
            Achievement.check_and_unlock(user, 'workouts_10')
        if workout_count >= 50:
            Achievement.check_and_unlock(user, 'workouts_50')
        if workout_count >= 100:
            Achievement.check_and_unlock(user, 'workouts_100')
        if workout_count >= 500:
            Achievement.check_and_unlock(user, 'workouts_500')
        
        # Volume milestones
        if total_volume >= 10000:
            Achievement.check_and_unlock(user, 'volume_10k')
        if total_volume >= 100000:
            Achievement.check_and_unlock(user, 'volume_100k')
        if total_volume >= 1000000:
            Achievement.check_and_unlock(user, 'volume_1m')
        
        # Streak achievements
        streak = self.calculate_streak(user)
        if streak >= 7:
            Achievement.check_and_unlock(user, 'streak_7')
        if streak >= 30:
            Achievement.check_and_unlock(user, 'streak_30')
        if streak >= 100:
            Achievement.check_and_unlock(user, 'streak_100')
        
        # PR achievements
        pr_count = Exercise.objects.filter(sets__workout__user=user).distinct().count()
        if pr_count >= 1:
            Achievement.check_and_unlock(user, 'first_pr')
        if pr_count >= 10:
            Achievement.check_and_unlock(user, 'prs_10')
        if pr_count >= 50:
            Achievement.check_and_unlock(user, 'prs_50')
        
        # Strength milestones
        self.check_strength_achievements(user)
        
        # Body tracking
        if BodyMeasurement.objects.filter(user=user).exists():
            Achievement.check_and_unlock(user, 'first_measurement')
        if BodyWeight.objects.filter(user=user).count() >= 30:
            Achievement.check_and_unlock(user, 'weight_logged_30')
    
    def calculate_streak(self, user):
        """Calculate current workout streak for user."""
        from datetime import timedelta
        
        today = timezone.now().date()
        dates = set(Workout.objects.filter(user=user).values_list('date', flat=True))
        
        streak = 0
        check_date = today
        
        # If no workout today, start from yesterday
        if check_date not in dates:
            check_date -= timedelta(days=1)
        
        # Count consecutive days
        while check_date in dates:
            streak += 1
            check_date -= timedelta(days=1)
        
        return streak
    
    def check_strength_achievements(self, user):
        """Check strength milestone achievements for user."""
        try:
            # Bench Press 100kg
            bench = Exercise.objects.filter(name__icontains='bench press').first()
            if bench:
                pb = bench.get_personal_best(user)
                if pb and pb.weight >= 100:
                    Achievement.check_and_unlock(user, 'bench_100')
            
            # Squat 140kg
            squat = Exercise.objects.filter(name__icontains='squat').exclude(name__icontains='split').first()
            if squat:
                pb = squat.get_personal_best(user)
                if pb and pb.weight >= 140:
                    Achievement.check_and_unlock(user, 'squat_140')
            
            # Deadlift 180kg
            deadlift = Exercise.objects.filter(name__icontains='deadlift').first()
            if deadlift:
                pb = deadlift.get_personal_best(user)
                if pb and pb.weight >= 180:
                    Achievement.check_and_unlock(user, 'deadlift_180')
            
            # OHP 60kg
            ohp = Exercise.objects.filter(name__icontains='overhead press').first()
            if ohp:
                pb = ohp.get_personal_best(user)
                if pb and pb.weight >= 60:
                    Achievement.check_and_unlock(user, 'ohp_60')
        except:
            pass
