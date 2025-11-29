# apps/attendance/models.py
from django.db import models
from apps.students.models import Student
from apps.courses.models import Course, Enrollment
from datetime import date


class Attendance(models.Model):
    """Attendance tracking model"""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused Absence'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        blank=True,
        null=True
    )
    
    # Attendance details
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Time tracking
    check_in_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for absence or additional notes"
    )
    
    # Recorded by
    recorded_by = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Staff member who recorded attendance"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'course', 'date')
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['course', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
        ordering = ['-date', 'student__full_name']
        verbose_name_plural = 'Attendance records'
    
    def __str__(self):
        return f"{self.student.full_name} - {self.course.course_name} - {self.date} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-populate enrollment if not provided
        if not self.enrollment:
            try:
                self.enrollment = Enrollment.objects.get(
                    student=self.student,
                    course=self.course,
                    status='active'
                )
            except Enrollment.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class AttendanceSummary(models.Model):
    """Monthly attendance summary for students"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_summaries'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendance_summaries'
    )
    
    # Period
    month = models.DateField(help_text="First day of the month")
    
    # Counts
    total_sessions = models.PositiveIntegerField(default=0)
    present_count = models.PositiveIntegerField(default=0)
    absent_count = models.PositiveIntegerField(default=0)
    late_count = models.PositiveIntegerField(default=0)
    excused_count = models.PositiveIntegerField(default=0)
    
    # Calculated
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Percentage of attendance (present + late) / total"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'course', 'month')
        indexes = [
            models.Index(fields=['student', 'month']),
            models.Index(fields=['course', 'month']),
            models.Index(fields=['month']),
        ]
        ordering = ['-month', 'student__full_name']
        verbose_name_plural = 'Attendance summaries'
    
    def __str__(self):
        return f"{self.student.full_name} - {self.course.course_name} - {self.month.strftime('%B %Y')}"
    
    def calculate_summary(self):
        """Calculate attendance summary from records"""
        from django.db.models import Count, Q
        
        # Get attendance records for the month
        records = Attendance.objects.filter(
            student=self.student,
            course=self.course,
            date__year=self.month.year,
            date__month=self.month.month
        )
        
        # Count by status
        counts = records.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late')),
            excused=Count('id', filter=Q(status='excused'))
        )
        
        self.total_sessions = counts['total'] or 0
        self.present_count = counts['present'] or 0
        self.absent_count = counts['absent'] or 0
        self.late_count = counts['late'] or 0
        self.excused_count = counts['excused'] or 0
        
        # Calculate attendance rate
        if self.total_sessions > 0:
            attended = self.present_count + self.late_count
            self.attendance_rate = (attended / self.total_sessions) * 100
        else:
            self.attendance_rate = 0
        
        self.save()