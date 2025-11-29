# apps/students/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model"""
    list_display = [
        'full_name', 'parent_name', 'parent_phone', 
        'education_level', 'status', 'active_enrollments', 
        'registration_date'
    ]
    list_filter = [
        'status', 'education_level', 'gender', 
        'registration_date', 'created_at'
    ]
    search_fields = [
        'full_name', 'parent_name', 'parent_phone', 
        'email', 'parent_email'
    ]
    date_hierarchy = 'registration_date'
    ordering = ['-registration_date', 'full_name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'full_name', 'date_of_birth', 'gender', 
                'email', 'phone', 'address'
            )
        }),
        ('Parent/Guardian Information', {
            'fields': (
                'parent_name', 'parent_phone', 'parent_email'
            )
        }),
        ('Educational Information', {
            'fields': (
                'education_level', 'school_name'
            )
        }),
        ('Registration Details', {
            'fields': (
                'registration_date', 'status'
            )
        }),
        ('Additional Information', {
            'fields': (
                'medical_notes', 'notes'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    list_per_page = 25
    
    actions = [
        'activate_students', 
        'deactivate_students', 
        'export_as_csv'
    ]
    
    def active_enrollments(self, obj):
        count = obj.enrollments.filter(status='active').count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                count
            )
        return count
    active_enrollments.short_description = 'Active Enrollments'
    
    def activate_students(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(
            request, 
            f'{updated} student(s) activated successfully.'
        )
    activate_students.short_description = 'Activate selected students'
    
    def deactivate_students(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(
            request, 
            f'{updated} student(s) deactivated successfully.'
        )
    deactivate_students.short_description = 'Deactivate selected students'
    
    def export_as_csv(self, request, queryset):
        # Implementation for CSV export
        pass
    export_as_csv.short_description = 'Export selected as CSV'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            enrollment_count=Count(
                'enrollments', 
                filter=Q(enrollments__status='active')
            )
        )
        return qs