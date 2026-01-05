"""
Views for gym workout tracking.
Provides functionality to:
- List all workout sessions
- View session details
- Create new sessions with sets
- View personal bests per exercise
- Manage exercises
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Max, Count
from django.utils import timezone

from .models import Exercise, WorkoutSession, Set
from .forms import ExerciseForm, WorkoutSessionForm, SetForm, QuickSetFormSet


class DashboardView(View):
    """
    Main dashboard showing recent workouts and quick stats.
    """
    def get(self, request):
        recent_sessions = WorkoutSession.objects.prefetch_related('sets__exercise')[:5]
        exercises = Exercise.objects.annotate(
            set_count=Count('sets'),
            max_weight=Max('sets__weight')
        ).order_by('-set_count')[:10]
        
        # Calculate some stats
        total_sessions = WorkoutSession.objects.count()
        total_sets = Set.objects.count()
        
        context = {
            'recent_sessions': recent_sessions,
            'exercises': exercises,
            'total_sessions': total_sessions,
            'total_sets': total_sets,
        }
        return render(request, 'workouts/dashboard.html', context)


class SessionListView(ListView):
    """
    List all workout sessions.
    """
    model = WorkoutSession
    template_name = 'workouts/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        return WorkoutSession.objects.prefetch_related('sets__exercise').all()


class SessionDetailView(DetailView):
    """
    View details of a specific workout session.
    """
    model = WorkoutSession
    template_name = 'workouts/session_detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sets_by_exercise'] = self.object.get_sets_by_exercise()
        context['total_volume'] = self.object.get_total_volume()
        return context


class SessionCreateView(View):
    """
    Create a new workout session with multiple sets.
    """
    def get(self, request):
        session_form = WorkoutSessionForm(initial={'date': timezone.now().date()})
        exercises = Exercise.objects.all()
        
        context = {
            'session_form': session_form,
            'exercises': exercises,
        }
        return render(request, 'workouts/session_create.html', context)

    def post(self, request):
        session_form = WorkoutSessionForm(request.POST)
        
        if session_form.is_valid():
            session = session_form.save()
            
            # Process sets from the form
            exercise_ids = request.POST.getlist('exercise')
            weights = request.POST.getlist('weight')
            reps_list = request.POST.getlist('reps')
            notes_list = request.POST.getlist('set_notes')
            
            sets_created = 0
            for i in range(len(exercise_ids)):
                if exercise_ids[i] and weights[i] and reps_list[i]:
                    try:
                        Set.objects.create(
                            session=session,
                            exercise_id=int(exercise_ids[i]),
                            weight=float(weights[i]),
                            reps=int(reps_list[i]),
                            notes=notes_list[i] if i < len(notes_list) else ''
                        )
                        sets_created += 1
                    except (ValueError, Exercise.DoesNotExist):
                        continue
            
            messages.success(request, f'Workout session created with {sets_created} sets!')
            return redirect('session_detail', pk=session.pk)
        
        exercises = Exercise.objects.all()
        context = {
            'session_form': session_form,
            'exercises': exercises,
        }
        return render(request, 'workouts/session_create.html', context)


class SessionDeleteView(DeleteView):
    """
    Delete a workout session.
    """
    model = WorkoutSession
    template_name = 'workouts/session_confirm_delete.html'
    success_url = reverse_lazy('session_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Workout session deleted.')
        return super().delete(request, *args, **kwargs)


class AddSetToSessionView(View):
    """
    Add additional sets to an existing session.
    """
    def get(self, request, session_id):
        session = get_object_or_404(WorkoutSession, pk=session_id)
        exercises = Exercise.objects.all()
        
        context = {
            'session': session,
            'exercises': exercises,
        }
        return render(request, 'workouts/add_set.html', context)

    def post(self, request, session_id):
        session = get_object_or_404(WorkoutSession, pk=session_id)
        
        exercise_id = request.POST.get('exercise')
        weight = request.POST.get('weight')
        reps = request.POST.get('reps')
        notes = request.POST.get('notes', '')

        try:
            Set.objects.create(
                session=session,
                exercise_id=int(exercise_id),
                weight=float(weight),
                reps=int(reps),
                notes=notes
            )
            messages.success(request, 'Set added successfully!')
        except (ValueError, Exercise.DoesNotExist) as e:
            messages.error(request, f'Error adding set: {e}')
        
        return redirect('session_detail', pk=session_id)


class DeleteSetView(View):
    """
    Delete a single set from a session.
    """
    def post(self, request, set_id):
        set_obj = get_object_or_404(Set, pk=set_id)
        session_id = set_obj.session.id
        set_obj.delete()
        messages.success(request, 'Set deleted.')
        return redirect('session_detail', pk=session_id)


class ExerciseListView(ListView):
    """
    List all exercises with their personal bests.
    """
    model = Exercise
    template_name = 'workouts/exercise_list.html'
    context_object_name = 'exercises'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get sort preference from query params
        sort_by = self.request.GET.get('sort', 'weight')
        context['sort_by'] = sort_by
        return context


class ExerciseDetailView(DetailView):
    """
    View details of a specific exercise including personal bests and history.
    """
    model = Exercise
    template_name = 'workouts/exercise_detail.html'
    context_object_name = 'exercise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = self.object
        
        context['pb_weight'] = exercise.get_personal_best_weight()
        context['pb_reps'] = exercise.get_personal_best_reps()
        context['progression'] = exercise.get_suggested_progression()
        context['recent_history'] = exercise.get_recent_history(limit=10)
        
        return context


class ExerciseCreateView(CreateView):
    """
    Create a new exercise.
    """
    model = Exercise
    form_class = ExerciseForm
    template_name = 'workouts/exercise_form.html'
    success_url = reverse_lazy('exercise_list')

    def form_valid(self, form):
        messages.success(self.request, f'Exercise "{form.instance.name}" created!')
        return super().form_valid(form)


class ExerciseDeleteView(DeleteView):
    """
    Delete an exercise.
    """
    model = Exercise
    template_name = 'workouts/exercise_confirm_delete.html'
    success_url = reverse_lazy('exercise_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Exercise deleted.')
        return super().delete(request, *args, **kwargs)


class PersonalBestsView(View):
    """
    View all personal bests across all exercises.
    Supports toggling between highest weight and highest reps.
    """
    def get(self, request):
        sort_by = request.GET.get('sort', 'weight')  # 'weight' or 'reps'
        
        exercises = Exercise.objects.annotate(set_count=Count('sets')).filter(set_count__gt=0)
        
        personal_bests = []
        for exercise in exercises:
            if sort_by == 'reps':
                pb = exercise.get_personal_best_reps()
            else:
                pb = exercise.get_personal_best_weight()
            
            if pb:
                personal_bests.append({
                    'exercise': exercise,
                    'weight': pb['weight'],
                    'reps': pb['reps'],
                    'date': pb['date'],
                    'progression': exercise.get_suggested_progression()
                })
        
        # Sort by weight or reps
        if sort_by == 'reps':
            personal_bests.sort(key=lambda x: x['reps'], reverse=True)
        else:
            personal_bests.sort(key=lambda x: x['weight'], reverse=True)
        
        context = {
            'personal_bests': personal_bests,
            'sort_by': sort_by,
        }
        return render(request, 'workouts/personal_bests.html', context)


# API-style views for AJAX requests
class ExerciseSuggestionsAPI(View):
    """
    Returns exercise suggestions for autocomplete.
    """
    def get(self, request):
        query = request.GET.get('q', '')
        exercises = Exercise.objects.filter(name__icontains=query)[:10]
        data = [{'id': e.id, 'name': e.name} for e in exercises]
        return JsonResponse({'exercises': data})


class ExerciseProgressionAPI(View):
    """
    Returns progression suggestion for a specific exercise.
    """
    def get(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, pk=exercise_id)
        progression = exercise.get_suggested_progression()
        
        if progression:
            return JsonResponse({
                'success': True,
                'suggested_weight': float(progression['suggested_weight']),
                'message': progression['message']
            })
        return JsonResponse({
            'success': False,
            'message': 'No previous data for this exercise'
        })
