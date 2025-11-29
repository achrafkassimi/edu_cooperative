# apps/attendance/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import Attendance, AttendanceSummary


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin interface for Attendance model"""
    list_display = [
        'student', 'course', 'date', 'status_badge', 
        'check_in_time', 'recorded_by'
    ]
    list_filter = [
        'status', 'date', 'course__course_type'
    ]
    search_fields = [
        'student__full_name', 'course__course_name', 
        'notes'
    ]
    date_hierarchy = 'date'
    ordering = ['-date', 'course', 'student__full_name']
    
    fieldsets = (
        ('Attendance Details', {
            'fields': (
                'student', 'course', 'enrollment', 
                'date', 'status'
            )
        }),
        ('Time Tracking', {
            'fields': (
                'check_in_time', 'check_out_time'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes', 'recorded_by'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    autocomplete_fields = ['student', 'course', 'enrollment']
    
    list_per_page = 50
    
    actions = [
        'mark_as_present', 
        'mark_as_absent', 
        'mark_as_excused'
    ]
    
    def status_badge(self, obj):
        colors = {
            'present': 'green',
            'absent': 'red',
            'late': 'orange',
            'excused': 'blue'
        }
        icons = {
            'present': '✓',
            'absent': '✗',
            'late': '⚠',
            'excused': 'ℹ'
        }
        color = colors.get(obj.status, 'gray')
        icon = icons.get(obj.status, '?')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_as_present(self, request, queryset):
        updated = queryset.update(status='present')
        self.message_user(
            request, 
            f'{updated} record(s) marked as present.'
        )
    mark_as_present.short_description = 'Mark as Present'
    
    def mark_as_absent(self, request, queryset):
        updated = queryset.update(status='absent')
        self.message_user(
            request, 
            f'{updated} record(s) marked as absent.'
        )
    mark_as_absent.short_description = 'Mark as Absent'
    
    def mark_as_excused(self, request, queryset):
        updated = queryset.update(status='excused')
        self.message_user(
            request, 
            f'{updated} record(s) marked as excused.'
        )
    mark_as_excused.short_description = 'Mark as Excused'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('student', 'course', 'enrollment')
        return qs


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    """Admin interface for AttendanceSummary"""
    list_display = [
        'student', 'course', 'month', 
        'total_sessions', 'attendance_rate_display', 
        'present_count', 'absent_count'
    ]
    list_filter = [
        'month', 'course__course_type'
    ]
    search_fields = [
        'student__full_name', 'course__course_name'
    ]
    date_hierarchy = 'month'
    ordering = ['-month', 'student__full_name']
    
    fieldsets = (
        ('Summary Details', {
            'fields': (
                'student', 'course', 'month'
            )
        }),
        ('Attendance Counts', {
            'fields': (
                'total_sessions', 'present_count', 'absent_count',
                'late_count', 'excused_count', 'attendance_rate'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'total_sessions', 'present_count', 'absent_count',
        'late_count', 'excused_count', 'attendance_rate',
        'created_at', 'updated_at'
    ]
    
    autocomplete_fields = ['student', 'course']
    
    list_per_page = 50
    
    actions = ['recalculate_summaries']
    
    def attendance_rate_display(self, obj):
        rate = obj.attendance_rate
        color = 'green' if rate >= 80 else 'orange' if rate >= 60 else 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, rate
        )
    attendance_rate_display.short_description = 'Attendance Rate'
    
    def recalculate_summaries(self, request, queryset):
        count = 0
        for summary in queryset:
            summary.calculate_summary()
            count += 1
        
        self.message_user(
            request, 
            f'{count} summary/summaries recalculated.'
        )
    recalculate_summaries.short_description = 'Recalculate selected summaries'
    
    def has_add_permission(self, request):
        return False