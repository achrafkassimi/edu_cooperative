# apps/courses/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Course, CourseInstructor, Enrollment


class CourseInstructorInline(admin.TabularInline):
    """Inline for course instructors"""
    model = CourseInstructor
    extra = 1
    fields = [
        'instructor', 'is_primary', 'hours_taught', 'notes'
    ]
    autocomplete_fields = ['instructor']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model"""
    list_display = [
        'course_name', 'subject', 'course_type', 
        'instructor_names', 'enrollment_status', 
        'fee_per_month', 'status', 'start_date'
    ]
    list_filter = [
        'course_type', 'status', 'subject', 
        'start_date', 'created_at'
    ]
    search_fields = [
        'course_name', 'subject', 'description'
    ]
    date_hierarchy = 'start_date'
    ordering = ['-start_date', 'course_name']
    
    fieldsets = (
        ('Course Information', {
            'fields': (
                'course_name', 'course_type', 'subject', 'description'
            )
        }),
        ('Financial Details', {
            'fields': (
                'fee_per_month', 'duration_months'
            )
        }),
        ('Capacity', {
            'fields': ('max_students',)
        }),
        ('Schedule', {
            'fields': (
                'schedule_days', 'schedule_time', 
                'hours_per_session', 'classroom'
            )
        }),
        ('Duration', {
            'fields': (
                'start_date', 'end_date', 'status'
            )
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
    
    inlines = [CourseInstructorInline]
    
    list_per_page = 25
    
    actions = [
        'activate_courses', 
        'complete_courses', 
        'cancel_courses'
    ]
    
    def instructor_names(self, obj):
        instructors = obj.course_instructors.select_related('instructor')
        names = []
        for ci in instructors:
            if ci.is_primary:
                names.append(f"<strong>{ci.instructor.full_name}</strong>")
            else:
                names.append(ci.instructor.full_name)
        return format_html('<br>'.join(names)) if names else '-'
    instructor_names.short_description = 'Instructors'
    
    def enrollment_status(self, obj):
        enrolled = obj.enrollments.filter(status='active').count()
        max_students = obj.max_students
        percentage = (enrolled / max_students * 100) if max_students > 0 else 0
        
        color = 'green' if percentage < 80 else 'orange' if percentage < 100 else 'red'
        
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color, enrolled, max_students, int(percentage)
        )
    enrollment_status.short_description = 'Enrollment'
    
    def activate_courses(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(
            request, 
            f'{updated} course(s) activated successfully.'
        )
    activate_courses.short_description = 'Activate selected courses'
    
    def complete_courses(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(
            request, 
            f'{updated} course(s) marked as completed.'
        )
    complete_courses.short_description = 'Mark selected as completed'
    
    def cancel_courses(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(
            request, 
            f'{updated} course(s) cancelled.'
        )
    cancel_courses.short_description = 'Cancel selected courses'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('course_instructors__instructor')
        return qs


@admin.register(CourseInstructor)
class CourseInstructorAdmin(admin.ModelAdmin):
    """Admin interface for CourseInstructor"""
    list_display = [
        'instructor', 'course', 'is_primary', 
        'hours_taught', 'assigned_date'
    ]
    list_filter = [
        'is_primary', 'assigned_date'
    ]
    search_fields = [
        'instructor__full_name', 'course__course_name'
    ]
    date_hierarchy = 'assigned_date'
    
    autocomplete_fields = ['course', 'instructor']
    
    readonly_fields = ['assigned_date', 'created_at', 'updated_at']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin interface for Enrollment"""
    list_display = [
        'student', 'course', 'enrollment_date', 
        'status', 'final_grade', 'completion_date'
    ]
    list_filter = [
        'status', 'enrollment_date', 'completion_date'
    ]
    search_fields = [
        'student__full_name', 'course__course_name'
    ]
    date_hierarchy = 'enrollment_date'
    ordering = ['-enrollment_date']
    
    fieldsets = (
        ('Enrollment Details', {
            'fields': (
                'student', 'course', 'enrollment_date', 'status'
            )
        }),
        ('Completion', {
            'fields': (
                'final_grade', 'completion_date'
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
    
    readonly_fields = ['enrollment_date', 'created_at', 'updated_at']
    
    autocomplete_fields = ['student', 'course']
    
    list_per_page = 25
    
    actions = [
        'activate_enrollments', 
        'complete_enrollments', 
        'suspend_enrollments'
    ]
    
    def activate_enrollments(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(
            request, 
            f'{updated} enrollment(s) activated.'
        )
    activate_enrollments.short_description = 'Activate selected enrollments'
    
    def complete_enrollments(self, request, queryset):
        from datetime import date
        updated = queryset.update(
            status='completed', 
            completion_date=date.today()
        )
        self.message_user(
            request, 
            f'{updated} enrollment(s) marked as completed.'
        )
    complete_enrollments.short_description = 'Mark selected as completed'
    
    def suspend_enrollments(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(
            request, 
            f'{updated} enrollment(s) suspended.'
        )
    suspend_enrollments.short_description = 'Suspend selected enrollments'