from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Custom user with a role flag distinguishing parents from teachers."""

    class Role(models.TextChoices):
        PARENT = 'parent', 'Parent / Guardian'
        TEACHER = 'teacher', 'Teacher'
        ADMIN = 'admin', 'Platform Admin'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PARENT)
    phone_number = models.CharField(max_length=20, blank=True)

    def is_parent(self):
        return self.role == self.Role.PARENT

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def __str__(self):
        return self.get_full_name() or self.username


SUBJECT_CHOICES = [
    ('piano', 'Piano'),
    ('guitar', 'Guitar'),
    ('violin', 'Violin'),
    ('voice', 'Voice / Singing'),
    ('math', 'Math Tutoring'),
    ('reading', 'Reading / Literacy'),
    ('science', 'Science Tutoring'),
    ('coding', 'Coding for Kids'),
    ('art', 'Art & Drawing'),
    ('swimming', 'Swimming'),
    ('chess', 'Chess'),
    ('dance', 'Dance'),
    ('other', 'Other'),
]

DAY_CHOICES = [
    (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
    (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
]


class TeacherProfile(models.Model):
    """Extra hire-able info for users with role == teacher."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='teacher_profile')
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    headline = models.CharField(max_length=120, help_text="e.g. 'Patient piano teacher for ages 5-12'")
    bio = models.TextField(help_text="Tell parents about your experience and teaching style.")
    years_experience = models.PositiveSmallIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2,
                                       validators=[MinValueValidator(0)])
    photo = models.ImageField(upload_to='teacher_photos/', blank=True, null=True)
    background_check_doc = models.FileField(upload_to='background_checks/', blank=True, null=True,
                                              help_text="Optional: upload proof of background check.")
    is_verified = models.BooleanField(
        default=False,
        help_text="Only verified teachers are publicly bookable. Set by an admin."
    )
    min_student_age = models.PositiveSmallIntegerField(default=4)
    max_student_age = models.PositiveSmallIntegerField(default=17)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_subject_display()})"

    def average_rating(self):
        agg = self.reviews.aggregate(models.Avg('rating'))
        avg = agg['rating__avg']
        return round(avg, 1) if avg else None

    def review_count(self):
        return self.reviews.count()

    def get_absolute_url(self):
        return reverse('teacher_detail', args=[self.pk])


class Availability(models.Model):
    """A recurring weekly slot when a teacher is free to teach."""

    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name_plural = 'Availabilities'

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}"


class Child(models.Model):
    """A parent's child who will receive the lessons."""

    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='children')
    full_name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(18)])
    notes = models.TextField(blank=True, help_text="Allergies, learning needs, interests, etc.")

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.age})"


class Booking(models.Model):
    """A parent's request to hire a teacher for their child at a given slot/date."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        DECLINED = 'declined', 'Declined'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='bookings')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='bookings')
    availability = models.ForeignKey(Availability, on_delete=models.SET_NULL, null=True, related_name='bookings')
    lesson_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    parent_message = models.TextField(blank=True, help_text="Anything the teacher should know up front.")
    teacher_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-lesson_date', '-created_at']

    def __str__(self):
        return f"{self.child.full_name} with {self.teacher} on {self.lesson_date} [{self.status}]"

    def can_be_reviewed(self):
        return self.status == self.Status.COMPLETED and not hasattr(self, 'review')


class Review(models.Model):
    """A parent's rating/comment about a teacher, tied to one completed booking."""

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='reviews')
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_written')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ for {self.teacher} by {self.parent}"
