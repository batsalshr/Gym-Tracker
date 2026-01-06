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
        ('cardio', 'Cardio'),
        ('glutes', 'Glutes'),
        ('forearms', 'Forearms'),
        ('calves', 'Calves'),
        ('traps', 'Traps'),
    ]
    
    name = models.CharField(max_length=100)
    muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUPS)
    equipment = models.CharField(max_length=50, blank=True, default='')  # barbell, dumbbell, machine, etc.
    
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
    
    date = models.DateField(default=timezone.now)
    muscle_groups = models.CharField(max_length=100, default='')
    notes = models.TextField(blank=True, default='')
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_muscle_groups_display()} - {self.date.strftime('%b %d, %Y')}"
    
    def get_muscle_groups_list(self):
        """Get list of muscle groups."""
        if not self.muscle_groups:
            return []
        return [mg.strip() for mg in self.muscle_groups.split(',') if mg.strip()]
    
    def get_muscle_groups_display(self):
        """Get display names for muscle groups."""
        groups = self.get_muscle_groups_list()
        display_map = dict(Exercise.MUSCLE_GROUPS)
        return ' & '.join(display_map.get(g, g.title()) for g in groups)
    
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


class BodyWeight(models.Model):
    """Track body weight over time."""
    date = models.DateField(default=timezone.now, unique=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # kg
    notes = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.weight}kg on {self.date}"


class WorkoutTemplate(models.Model):
    """Saved workout template for quick logging."""
    name = models.CharField(max_length=100, unique=True)
    muscle_groups = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_muscle_groups_display(self):
        groups = [mg.strip() for mg in self.muscle_groups.split(',') if mg.strip()]
        display_map = dict(Exercise.MUSCLE_GROUPS)
        return ' & '.join(display_map.get(g, g.title()) for g in groups)


class TemplateExercise(models.Model):
    """Exercise in a workout template."""
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    target_sets = models.PositiveIntegerField(default=3)
    target_reps = models.CharField(max_length=20, default='8-12')  # e.g., "8-12" or "5"
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.exercise.name} ({self.target_sets}x{self.target_reps})"


class Goal(models.Model):
    """Strength or fitness goal."""
    GOAL_TYPES = [
        ('weight', 'Lift Weight'),
        ('reps', 'Reps at Weight'),
        ('bodyweight', 'Body Weight'),
        ('volume', 'Weekly Volume'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('achieved', 'Achieved'),
        ('abandoned', 'Abandoned'),
    ]
    
    name = models.CharField(max_length=100)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=True, blank=True)
    target_value = models.DecimalField(max_digits=8, decimal_places=2)
    target_reps = models.PositiveIntegerField(null=True, blank=True)  # For "reps at weight" goals
    current_value = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    achieved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_progress_percent(self):
        if self.target_value == 0:
            return 0
        return min(100, int((self.current_value / self.target_value) * 100))
    
    def update_progress(self):
        """Update current value based on goal type."""
        if self.goal_type == 'weight' and self.exercise:
            pb = self.exercise.get_personal_best()
            if pb:
                self.current_value = pb.weight
        elif self.goal_type == 'bodyweight':
            latest = BodyWeight.objects.first()
            if latest:
                self.current_value = latest.weight
        
        # Check if achieved
        if self.current_value >= self.target_value:
            self.status = 'achieved'
            if not self.achieved_at:
                self.achieved_at = timezone.now()
        
        self.save()
