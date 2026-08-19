from django.contrib import admin
from .models import User, TeacherProfile, Availability, Child, Booking, Review
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class LessonHubUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('LessonHub', {'fields': ('role', 'phone_number')}),
    )


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'hourly_rate', 'is_verified', 'average_rating', 'created_at']
    list_filter = ['subject', 'is_verified']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'headline']
    actions = ['verify_teachers', 'unverify_teachers']
    inlines = [AvailabilityInline]

    @admin.action(description="Mark selected teachers as verified")
    def verify_teachers(self, request, queryset):
        queryset.update(is_verified=True)

    @admin.action(description="Mark selected teachers as NOT verified")
    def unverify_teachers(self, request, queryset):
        queryset.update(is_verified=False)


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'age', 'parent']
    search_fields = ['full_name', 'parent__username']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['child', 'teacher', 'parent', 'lesson_date', 'status']
    list_filter = ['status', 'lesson_date']
    search_fields = ['child__full_name', 'teacher__user__username', 'parent__username']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'parent', 'rating', 'created_at']
    list_filter = ['rating']


admin.site.register(Availability)
admin.site.site_header = "Learny Administration"
