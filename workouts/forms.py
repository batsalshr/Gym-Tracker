"""
Forms for gym workout tracking.
"""

from django import forms
from django.forms import formset_factory, inlineformset_factory
from .models import Exercise, WorkoutSession, Set


class ExerciseForm(forms.ModelForm):
    """
    Form for creating/editing exercises.
    """
    class Meta:
        model = Exercise
        fields = ['name', 'description', 'muscle_group']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bench Press'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description or notes'
            }),
            'muscle_group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Chest, Back, Legs'
            }),
        }


class WorkoutSessionForm(forms.ModelForm):
    """
    Form for creating/editing workout sessions.
    """
    class Meta:
        model = WorkoutSession
        fields = ['date', 'notes', 'duration_minutes']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes about this workout'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in minutes'
            }),
        }


class SetForm(forms.ModelForm):
    """
    Form for creating/editing individual sets.
    """
    class Meta:
        model = Set
        fields = ['exercise', 'weight', 'reps', 'notes']
        widgets = {
            'exercise': forms.Select(attrs={
                'class': 'form-control exercise-select'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0',
                'placeholder': 'kg'
            }),
            'reps': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'reps'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional notes'
            }),
        }


# Formset for adding multiple sets at once
QuickSetFormSet = formset_factory(SetForm, extra=5)


class QuickAddSetForm(forms.Form):
    """
    Simple form for quickly adding a set to an existing session.
    """
    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    weight = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'min': '0',
            'placeholder': 'Weight (kg)'
        })
    )
    reps = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'Reps'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional notes'
        })
    )
