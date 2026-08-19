from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:pk>/book/', views.book_teacher, name='book_teacher'),

    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/login/', views.LessonHubLoginView.as_view(), name='login'),
    path('accounts/logout/', views.LessonHubLogoutView.as_view(), name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),
    path('dashboard/parent/children/add/', views.child_add, name='child_add'),
    path('dashboard/parent/bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('dashboard/parent/bookings/<int:pk>/review/', views.leave_review, name='leave_review'),

    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/teacher/profile/', views.teacher_profile_edit, name='teacher_profile_edit'),
    path('dashboard/teacher/availability/add/', views.availability_add, name='availability_add'),
    path('dashboard/teacher/bookings/<int:pk>/respond/', views.respond_booking, name='respond_booking'),
]
