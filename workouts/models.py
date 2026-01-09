"""Models for gym workout tracking."""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
import random
import string


class UserProfile(models.Model):
    """Extended user profile with unique tracking ID."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tracking_id = models.CharField(max_length=12, unique=True, editable=False)
    display_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=200, blank=True)
    avatar_color = models.CharField(max_length=7, default='#3b82f6')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Stats
    total_workouts = models.PositiveIntegerField(default=0)
    total_volume = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = self.generate_unique_id()
        if not self.display_name:
            self.display_name = self.user.username
        super().save(*args, **kwargs)
    
    @property
    def user_id(self):
        """Alias for tracking_id for templates."""
        return self.tracking_id
    
    @staticmethod
    def generate_unique_id():
        """Generate a unique 8-character alphanumeric ID."""
        while True:
            # Format: IL-XXXXXX (IL prefix + 6 chars)
            chars = string.ascii_uppercase + string.digits
            new_id = 'IL-' + ''.join(random.choices(chars, k=6))
            if not UserProfile.objects.filter(tracking_id=new_id).exists():
                return new_id
    
    def get_initials(self):
        """Get user initials for avatar."""
        name = self.display_name or self.user.username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[:2].upper()
    
    def __str__(self):
        return f"{self.user.username} ({self.tracking_id})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create profile when user is created."""
    if created:
        # Generate random avatar color
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
        UserProfile.objects.create(user=instance, avatar_color=random.choice(colors))


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


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
    equipment = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    instructions = models.TextField(blank=True, default='')  # Store as JSON list
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # null = shared exercise
    
    class Meta:
        ordering = ['muscle_group', 'name']
    
    def __str__(self):
        return self.name
    
    def is_dumbbell(self):
        """Check if exercise uses dumbbells."""
        return self.equipment.lower() == 'dumbbell' if self.equipment else False
    
    def get_instructions_list(self):
        """Get instructions as a list."""
        if not self.instructions:
            return []
        try:
            import json
            return json.loads(self.instructions)
        except:
            return [self.instructions]
    
    def get_personal_best(self, user=None):
        """Get the heaviest weight lifted for this exercise."""
        sets = self.sets.all()
        if user:
            sets = sets.filter(workout__user=user)
        best = sets.order_by('-weight').first()
        return best
    
    def get_last_workout(self, user=None):
        """Get the most recent set for this exercise."""
        sets = self.sets.all()
        if user:
            sets = sets.filter(workout__user=user)
        return sets.order_by('-workout__date', '-id').first()
    
    def get_suggested_weight(self, user=None):
        """Suggest next weight based on last performance."""
        last = self.get_last_workout(user)
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
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
    weight = models.DecimalField(max_digits=6, decimal_places=2)  # Weight per hand for dumbbells
    reps = models.PositiveIntegerField()
    notes = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.weight}kg × {self.reps}"
    
    def is_dumbbell(self):
        """Check if exercise uses dumbbells."""
        return self.exercise.equipment.lower() == 'dumbbell' if self.exercise.equipment else False
    
    def get_total_weight(self):
        """Get total weight lifted (doubled for dumbbells)."""
        if self.is_dumbbell():
            return self.weight * 2
        return self.weight
    
    def get_volume(self):
        """Get volume (weight × reps), accounting for dumbbells."""
        return self.get_total_weight() * self.reps
    
    def get_display_weight(self):
        """Get weight for display with indicator if dumbbell."""
        if self.is_dumbbell():
            return f"{self.weight}kg ×2"
        return f"{self.weight}kg"


class BodyWeight(models.Model):
    """Track body weight over time."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # kg
    notes = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.weight}kg on {self.date}"


class WorkoutTemplate(models.Model):
    """Saved workout template for quick logging."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=True, blank=True)
    target_value = models.DecimalField(max_digits=8, decimal_places=2)
    target_reps = models.PositiveIntegerField(null=True, blank=True)
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
        if not self.target_value or self.target_value == 0:
            return 0
        try:
            return min(100, int((float(self.current_value) / float(self.target_value)) * 100))
        except (ValueError, TypeError):
            return 0
    
    def update_progress(self):
        """Update current value based on goal type."""
        from decimal import Decimal
        
        if self.goal_type == 'weight' and self.exercise:
            pb = self.exercise.get_personal_best()
            if pb:
                self.current_value = pb.weight
        elif self.goal_type == 'bodyweight':
            latest = BodyWeight.objects.first()
            if latest:
                self.current_value = latest.weight
        
        # Check if achieved - ensure both are Decimal for comparison
        try:
            current = Decimal(str(self.current_value)) if self.current_value else Decimal('0')
            target = Decimal(str(self.target_value)) if self.target_value else Decimal('0')
            
            if target > 0 and current >= target:
                self.status = 'achieved'
                if not self.achieved_at:
                    self.achieved_at = timezone.now()
        except (ValueError, TypeError):
            pass
        
        self.save()


class BodyMeasurement(models.Model):
    """Track body measurements over time."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    
    # Measurements in cm
    chest = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    waist = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    hips = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    left_arm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    right_arm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    left_thigh = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    right_thigh = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    left_calf = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    right_calf = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    shoulders = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    neck = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    # Calculated metrics
    body_fat_percent = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Measurements on {self.date}"
    
    def get_filled_fields(self):
        """Return list of measurements that have values."""
        fields = ['chest', 'waist', 'hips', 'left_arm', 'right_arm', 
                  'left_thigh', 'right_thigh', 'left_calf', 'right_calf', 
                  'shoulders', 'neck']
        return [(f, getattr(self, f)) for f in fields if getattr(self, f)]


class Achievement(models.Model):
    """Gamification achievements."""
    ACHIEVEMENT_TYPES = [
        # Workout milestones
        ('first_workout', 'First Workout'),
        ('workouts_10', '10 Workouts'),
        ('workouts_50', '50 Workouts'),
        ('workouts_100', '100 Workouts'),
        ('workouts_500', '500 Workouts'),
        
        # Streak achievements
        ('streak_7', '7-Day Streak'),
        ('streak_30', '30-Day Streak'),
        ('streak_100', '100-Day Streak'),
        
        # PR achievements
        ('first_pr', 'First PR'),
        ('prs_10', '10 PRs'),
        ('prs_50', '50 PRs'),
        
        # Volume achievements
        ('volume_10k', '10,000 kg Lifted'),
        ('volume_100k', '100,000 kg Lifted'),
        ('volume_1m', '1,000,000 kg Lifted'),
        
        # Strength milestones
        ('bench_100', 'Bench 100kg'),
        ('squat_140', 'Squat 140kg'),
        ('deadlift_180', 'Deadlift 180kg'),
        ('ohp_60', 'OHP 60kg'),
        
        # Consistency
        ('early_bird', 'Early Bird (5 AM workout)'),
        ('night_owl', 'Night Owl (10 PM workout)'),
        ('weekend_warrior', 'Weekend Warrior'),
        
        # Body
        ('first_measurement', 'First Measurement'),
        ('weight_logged_30', '30 Days Weight Logged'),
    ]
    
    ICONS = {
        'first_workout': 'fa-solid fa-flag-checkered', 
        'workouts_10': 'fa-solid fa-person-running', 
        'workouts_50': 'fa-solid fa-fire-flame-curved', 
        'workouts_100': 'fa-solid fa-star', 
        'workouts_500': 'fa-solid fa-crown',
        'streak_7': 'fa-solid fa-calendar-week', 
        'streak_30': 'fa-solid fa-calendar-check', 
        'streak_100': 'fa-solid fa-calendar-days',
        'first_pr': 'fa-solid fa-trophy', 
        'prs_10': 'fa-solid fa-medal', 
        'prs_50': 'fa-solid fa-gem',
        'volume_10k': 'fa-solid fa-dumbbell', 
        'volume_100k': 'fa-solid fa-weight-hanging', 
        'volume_1m': 'fa-solid fa-mountain',
        'bench_100': 'fa-solid fa-bullseye', 
        'squat_140': 'fa-solid fa-person-arrow-down-to-line', 
        'deadlift_180': 'fa-solid fa-arrow-up-from-ground-water', 
        'ohp_60': 'fa-solid fa-hands',
        'early_bird': 'fa-solid fa-sun', 
        'night_owl': 'fa-solid fa-moon', 
        'weekend_warrior': 'fa-solid fa-swords',
        'first_measurement': 'fa-solid fa-ruler', 
        'weight_logged_30': 'fa-solid fa-scale-balanced',
    }
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    unlocked = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-unlocked_at', 'achievement_type']
        unique_together = ['user', 'achievement_type']
    
    def __str__(self):
        return self.get_achievement_type_display()
    
    @property
    def icon(self):
        return self.ICONS.get(self.achievement_type, '🏅')
    
    @classmethod
    def check_and_unlock(cls, user, achievement_type):
        """Check and unlock an achievement for a user."""
        achievement, created = cls.objects.get_or_create(
            user=user, 
            achievement_type=achievement_type
        )
        if not achievement.unlocked:
            achievement.unlocked = True
            achievement.unlocked_at = timezone.now()
            achievement.save()
            return True
        return False
