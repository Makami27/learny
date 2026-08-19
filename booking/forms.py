from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, TeacherProfile, Availability, Child, Booking, Review


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=[(User.Role.PARENT, 'Parent / Guardian'),
                                       (User.Role.TEACHER, 'Teacher')])
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number',
                   'role', 'password1', 'password2']


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['subject', 'headline', 'bio', 'years_experience', 'hourly_rate',
                   'photo', 'min_student_age', 'max_student_age', 'background_check_doc']
        widgets = {'bio': forms.Textarea(attrs={'rows': 5})}


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['day_of_week', 'start_time', 'end_time', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['full_name', 'age', 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['child', 'availability', 'lesson_date', 'parent_message']
        widgets = {
            'lesson_date': forms.DateInput(attrs={'type': 'date'}),
            'parent_message': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, parent=None, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if parent is not None:
            self.fields['child'].queryset = Child.objects.filter(parent=parent)
        if teacher is not None:
            self.fields['availability'].queryset = Availability.objects.filter(
                teacher=teacher, is_active=True)


class BookingStatusForm(forms.ModelForm):
    """Used by the teacher to accept/decline a pending booking."""
    class Meta:
        model = Booking
        fields = ['status', 'teacher_response']
        widgets = {'teacher_response': forms.Textarea(attrs={'rows': 2})}


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
