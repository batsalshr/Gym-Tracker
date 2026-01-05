"""Models for gym workout tracking."""
from django.db import models
from django.utils import timezone
from decimal import Decimal


class Exercise(models.Model):
    """An exercise type (e.g., Bench Press, Squat)."""
    
    MUSCLE_GROUPS = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('shoulders', 'Shoulders'),
        ('legs', 'Legs'),
        ('biceps', 'Biceps'),
        ('triceps', 'Triceps'),
        ('core', 'Core'),
    ]
    
    name = models.CharField(max_length=100)
    muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUPS)
    
    class Meta:
        ordering = ['muscle_group', 'name']
        unique_together = ['name', 'muscle_group']
    
    def __str__(self):
        return self.name
    
    def get_personal_best(self):
        """Get the heaviest weight lifted for this exercise."""
        best = self.sets.order_by('-weight').first()
        return best
    
    def get_last_workout(self):
        """Get the most recent set for this exercise."""
        return self.sets.order_by('-workout__date', '-id').first()
    
    def get_suggested_weight(self):
        """Suggest next weight based on last performance."""
        last = self.get_last_workout()
        if not last:
            return None
        
        if last.reps >= 8:
            return last.weight + Decimal('2.5')
        elif last.reps >= 5:
            return last.weight
        else:
            return max(last.weight - Decimal('2.5'), Decimal('0'))


class Workout(models.Model):
    """A workout session."""
    
    DAY_TYPES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('shoulders', 'Shoulders'),
        ('legs', 'Legs'),
        ('biceps', 'Biceps'),
        ('triceps', 'Triceps'),
        ('chest_triceps', 'Chest & Triceps'),
        ('back_biceps', 'Back & Biceps'),
        ('push', 'Push'),
        ('pull', 'Pull'),
        ('upper', 'Upper Body'),
        ('lower', 'Lower Body'),
        ('full', 'Full Body'),
    ]
    
    date = models.DateField(default=timezone.now)
    day_type = models.CharField(max_length=20, choices=DAY_TYPES)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_day_type_display()} - {self.date.strftime('%b %d, %Y')}"
    
    def get_total_sets(self):
        return self.sets.count()
    
    def get_total_volume(self):
        """Total weight × reps."""
        return sum(s.weight * s.reps for s in self.sets.all())
    
    def get_exercises_summary(self):
        """Get unique exercises with set counts."""
        exercises = {}
        for s in self.sets.select_related('exercise').all():
            if s.exercise.name not in exercises:
                exercises[s.exercise.name] = {'sets': [], 'exercise': s.exercise}
            exercises[s.exercise.name]['sets'].append(s)
        return exercises
    
    def get_primary_exercise(self):
        """Get the first/main exercise of the workout."""
        first_set = self.sets.first()
        return first_set.exercise.name if first_set else "No exercises"


class Set(models.Model):
    """A single set within a workout."""
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='sets')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='sets')
    set_number = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    reps = models.PositiveIntegerField()
    notes = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.weight}kg × {self.reps}"
    
    def get_volume(self):
        return self.weight * self.reps
