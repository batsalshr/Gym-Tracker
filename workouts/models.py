"""
Models for gym workout tracking.

Exercise - Types of exercises (Bench Press, Deadlift, etc.)
WorkoutSession - Individual workout sessions linked to a date
Set - Individual sets within a session, linked to an exercise
"""

from django.db import models
from django.utils import timezone
from decimal import Decimal


class Exercise(models.Model):
    """
    Represents a type of exercise (e.g., Bench Press, Deadlift, Squat).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text="Optional description or notes about the exercise")
    muscle_group = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Primary muscle group targeted (e.g., Chest, Back, Legs)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_personal_best_weight(self):
        """
        Returns the personal best (highest weight lifted) for this exercise.
        Returns a dictionary with weight, reps, and the date achieved.
        """
        best_set = self.sets.order_by('-weight', '-reps').first()
        if best_set:
            return {
                'weight': best_set.weight,
                'reps': best_set.reps,
                'date': best_set.session.date,
                'set': best_set
            }
        return None

    def get_personal_best_reps(self):
        """
        Returns the best set by highest reps for this exercise.
        Returns a dictionary with weight, reps, and the date achieved.
        """
        best_set = self.sets.order_by('-reps', '-weight').first()
        if best_set:
            return {
                'weight': best_set.weight,
                'reps': best_set.reps,
                'date': best_set.session.date,
                'set': best_set
            }
        return None

    def get_suggested_progression(self):
        """
        Suggests weight progression based on the last workout.
        Rule: If you completed 8+ reps at a weight, suggest increasing by 2.5kg.
        If you completed less, suggest staying at the same weight.
        """
        last_set = self.sets.order_by('-session__date', '-id').first()
        if last_set:
            current_weight = last_set.weight
            last_reps = last_set.reps
            
            if last_reps >= 8:
                # Suggest 2.5kg increase (standard progression)
                suggested_weight = current_weight + Decimal('2.5')
                message = f"Great progress! Try {suggested_weight}kg (up from {current_weight}kg × {last_reps} reps)"
            elif last_reps >= 5:
                # Stay at same weight, aim for more reps
                suggested_weight = current_weight
                message = f"Aim for {current_weight}kg × 8 reps (last: {last_reps} reps)"
            else:
                # Consider deloading
                suggested_weight = max(current_weight - Decimal('2.5'), Decimal('0'))
                message = f"Consider {suggested_weight}kg for better form (struggling at {current_weight}kg × {last_reps})"
            
            return {
                'suggested_weight': suggested_weight,
                'last_weight': current_weight,
                'last_reps': last_reps,
                'last_date': last_set.session.date,
                'message': message
            }
        return None

    def get_recent_history(self, limit=5):
        """
        Returns the most recent sets for this exercise.
        """
        return self.sets.select_related('session').order_by('-session__date', '-id')[:limit]


class WorkoutSession(models.Model):
    """
    Represents a single workout session on a specific date.
    """
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, help_text="Optional notes about the session")
    duration_minutes = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Workout duration in minutes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Workout on {self.date.strftime('%Y-%m-%d')}"

    def get_exercises_performed(self):
        """
        Returns a list of unique exercises performed in this session.
        """
        return Exercise.objects.filter(sets__session=self).distinct()

    def get_total_volume(self):
        """
        Calculates total volume (weight × reps) for the session.
        """
        total = sum(s.weight * s.reps for s in self.sets.all())
        return total

    def get_sets_by_exercise(self):
        """
        Returns sets grouped by exercise for display.
        """
        exercises = {}
        for set_obj in self.sets.select_related('exercise').order_by('exercise__name', 'id'):
            exercise_name = set_obj.exercise.name
            if exercise_name not in exercises:
                exercises[exercise_name] = []
            exercises[exercise_name].append(set_obj)
        return exercises


class Set(models.Model):
    """
    Represents a single set within a workout session.
    """
    session = models.ForeignKey(
        WorkoutSession, 
        on_delete=models.CASCADE, 
        related_name='sets'
    )
    exercise = models.ForeignKey(
        Exercise, 
        on_delete=models.CASCADE, 
        related_name='sets'
    )
    weight = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Weight in kg"
    )
    reps = models.PositiveIntegerField(help_text="Number of repetitions")
    notes = models.TextField(blank=True, help_text="Optional notes (e.g., 'felt easy', 'form breakdown')")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.exercise.name}: {self.weight}kg × {self.reps}"

    def get_volume(self):
        """
        Returns the volume for this set (weight × reps).
        """
        return self.weight * self.reps

    def is_personal_best(self):
        """
        Checks if this set is the personal best (by weight) for the exercise.
        """
        pb = self.exercise.get_personal_best_weight()
        if pb and pb['set'].id == self.id:
            return True
        return False
