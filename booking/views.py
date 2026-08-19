from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q

from .forms import (SignUpForm, TeacherProfileForm, AvailabilityForm, ChildForm,
                     BookingForm, BookingStatusForm, ReviewForm)
from .models import TeacherProfile, Availability, Child, Booking, Review, SUBJECT_CHOICES, User


# ---------------------------------------------------------------- public ---

def home(request):
    featured = (TeacherProfile.objects.filter(is_verified=True)
                .order_by('-created_at')[:6])
    return render(request, 'booking/home.html', {'featured': featured})


def teacher_list(request):
    teachers = TeacherProfile.objects.filter(is_verified=True)
    subject = request.GET.get('subject', '')
    query = request.GET.get('q', '')
    if subject:
        teachers = teachers.filter(subject=subject)
    if query:
        teachers = teachers.filter(
            Q(headline__icontains=query) | Q(bio__icontains=query) |
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)
        )
    return render(request, 'booking/teacher_list.html', {
        'teachers': teachers, 'subjects': SUBJECT_CHOICES,
        'selected_subject': subject, 'query': query,
    })


def teacher_detail(request, pk):
    teacher = get_object_or_404(TeacherProfile, pk=pk)
    if not teacher.is_verified and not (request.user.is_authenticated and request.user == teacher.user):
        raise PermissionDenied("This teacher profile is not yet public.")
    availabilities = teacher.availabilities.filter(is_active=True)
    reviews = teacher.reviews.select_related('parent')[:10]
    return render(request, 'booking/teacher_detail.html', {
        'teacher': teacher, 'availabilities': availabilities, 'reviews': reviews,
    })


# --------------------------------------------------------------- account ---

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == User.Role.TEACHER:
                messages.info(request, "Welcome! Please complete your teacher profile so parents can find you.")
                return redirect('teacher_profile_edit')
            messages.success(request, "Welcome to Learny! Add your child to start booking lessons.")
            return redirect('child_add')
    else:
        form = SignUpForm()
    return render(request, 'booking/signup.html', {'form': form})


class LessonHubLoginView(LoginView):
    template_name = 'booking/login.html'


class LessonHubLogoutView(LogoutView):
    next_page = reverse_lazy('home')


@login_required
def dashboard(request):
    if request.user.is_teacher():
        return redirect('teacher_dashboard')
    return redirect('parent_dashboard')


# ----------------------------------------------------------------- parent --

@login_required
def parent_dashboard(request):
    if not request.user.is_parent():
        raise PermissionDenied
    children = request.user.children.all()
    bookings = request.user.bookings.select_related('teacher__user', 'child')
    return render(request, 'booking/parent_dashboard.html', {
        'children': children, 'bookings': bookings,
    })


@login_required
def child_add(request):
    if not request.user.is_parent():
        raise PermissionDenied
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user
            child.save()
            messages.success(request, f"Added {child.full_name}.")
            return redirect('parent_dashboard')
    else:
        form = ChildForm()
    return render(request, 'booking/child_form.html', {'form': form})


@login_required
def book_teacher(request, pk):
    if not request.user.is_parent():
        raise PermissionDenied
    teacher = get_object_or_404(TeacherProfile, pk=pk, is_verified=True)
    if not request.user.children.exists():
        messages.warning(request, "Add a child first so we know who the lesson is for.")
        return redirect('child_add')
    if request.method == 'POST':
        form = BookingForm(request.POST, parent=request.user, teacher=teacher)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.parent = request.user
            booking.teacher = teacher
            booking.save()
            messages.success(request, "Booking request sent! The teacher will respond soon.")
            return redirect('parent_dashboard')
    else:
        form = BookingForm(parent=request.user, teacher=teacher)
    return render(request, 'booking/book_teacher.html', {'form': form, 'teacher': teacher})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, parent=request.user)
    if request.method == 'POST':
        booking.status = Booking.Status.CANCELLED
        booking.save()
        messages.info(request, "Booking cancelled.")
    return redirect('parent_dashboard')


@login_required
def leave_review(request, pk):
    booking = get_object_or_404(Booking, pk=pk, parent=request.user)
    if not booking.can_be_reviewed():
        raise PermissionDenied("This booking can't be reviewed.")
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.teacher = booking.teacher
            review.parent = request.user
            review.save()
            messages.success(request, "Thanks for your review!")
            return redirect('parent_dashboard')
    else:
        form = ReviewForm()
    return render(request, 'booking/review_form.html', {'form': form, 'booking': booking})


# ---------------------------------------------------------------- teacher --

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher():
        raise PermissionDenied
    profile = getattr(request.user, 'teacher_profile', None)
    bookings = []
    if profile:
        bookings = profile.bookings.select_related('parent', 'child')
    return render(request, 'booking/teacher_dashboard.html', {
        'profile': profile, 'bookings': bookings,
    })


@login_required
def teacher_profile_edit(request):
    if not request.user.is_teacher():
        raise PermissionDenied
    profile = getattr(request.user, 'teacher_profile', None)
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile saved. An admin will verify it shortly.")
            return redirect('teacher_dashboard')
    else:
        form = TeacherProfileForm(instance=profile)
    return render(request, 'booking/teacher_profile_form.html', {'form': form})


@login_required
def availability_add(request):
    if not request.user.is_teacher():
        raise PermissionDenied
    profile = getattr(request.user, 'teacher_profile', None)
    if profile is None:
        messages.warning(request, "Complete your profile before setting availability.")
        return redirect('teacher_profile_edit')
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.teacher = profile
            slot.save()
            messages.success(request, "Availability added.")
            return redirect('teacher_dashboard')
    else:
        form = AvailabilityForm()
    return render(request, 'booking/availability_form.html', {'form': form})


@login_required
def respond_booking(request, pk):
    profile = getattr(request.user, 'teacher_profile', None)
    booking = get_object_or_404(Booking, pk=pk, teacher=profile)
    if request.method == 'POST':
        form = BookingStatusForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, f"Booking marked {booking.get_status_display()}.")
            return redirect('teacher_dashboard')
    else:
        form = BookingStatusForm(instance=booking)
    return render(request, 'booking/respond_booking.html', {'form': form, 'booking': booking})
