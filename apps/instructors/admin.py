# apps/instructors/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Instructor


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    """Admin interface for Instructor model"""
    list_display = [
        'full_name', 'specialization', 'employment_type', 
        'hourly_rate', 'active_courses_display', 
        'status', 'hire_date'
    ]
    list_filter = [
        'status', 'employment_type', 'specialization', 
        'hire_date', 'created_at'
    ]
    search_fields = [
        'full_name', 'email', 'phone', 
        'specialization'
    ]
    date_hierarchy = 'hire_date'
    ordering = ['full_name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'full_name', 'email', 'phone', 'address'
            )
        }),
        ('Professional Information', {
            'fields': (
                'specialization', 'qualifications', 
                'years_of_experience', 'bio'
            )
        }),
        ('Employment Details', {
            'fields': (
                'employment_type', 'hire_date', 'status'
            )
        }),
        ('Payment Information', {
            'fields': (
                'hourly_rate', 'tax_rate_percentage'
            )
        }),
        ('Banking Details', {
            'fields': (
                'bank_name', 'account_number', 'rib'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    list_per_page = 25
    
    actions = [
        'activate_instructors', 
        'deactivate_instructors'
    ]
    
    def active_courses_display(self, obj):
        count = obj.instructor_courses.filter(
            course__status='active'
        ).count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                count
            )
        return count
    active_courses_display.short_description = 'Active Courses'
    
    def activate_instructors(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(
            request, 
            f'{updated} instructor(s) activated successfully.'
        )
    activate_instructors.short_description = 'Activate selected instructors'
    
    def deactivate_instructors(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(
            request, 
            f'{updated} instructor(s) deactivated successfully.'
        )
    deactivate_instructors.short_description = 'Deactivate selected instructors'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            active_course_count=Count(
                'instructor_courses',
                filter=Q(instructor_courses__course__status='active')
            )
        )
        return qs