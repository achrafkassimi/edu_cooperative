# apps/courses/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.students.models import Student
from apps.instructors.models import Instructor


class Course(models.Model):
    """Course model"""
    COURSE_TYPE_CHOICES = [
        ('academic', 'Academic Support'),
        ('language', 'Language Course'),
        ('skill', 'Skill Development'),
        ('exam_prep', 'Exam Preparation'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]
    
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    # Course Information
    course_name = models.CharField(max_length=200, db_index = True)
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, db_index = True)
    subject = models.CharField(max_length=100, db_index = True)
    description = models.TextField(blank=True, null=True)
    
    # Financial
    fee_per_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Monthly fee in DH"
    )
    
    # Capacity
    max_students = models.PositiveIntegerField(
        default=20,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of students"
    )
    
    # Duration
    duration_months = models.PositiveIntegerField(
        default=1,
        help_text="Course duration in months"
    )
    
    # Schedule
    schedule_days = models.JSONField(
        default=list,
        help_text="List of days when course meets (e.g., ['monday', 'wednesday'])"
    )
    schedule_time = models.TimeField(help_text="Start time of the course")
    hours_per_session = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('1.5'),
        validators=[MinValueValidator(Decimal('0.5'))],
        help_text="Duration of each session in hours"
    )
    
    # Location
    classroom = models.CharField(max_length=50, blank=True, null=True)
    
    # Dates
    start_date = models.DateField(db_index = True)
    end_date = models.DateField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index = True)
    
    # Additional
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # db_index = True
        # indexes = [
        #     models.Index(fields=['course_name']),
        #     models.Index(fields=['course_type']),
        #     models.Index(fields=['status']),
        #     models.Index(fields=['start_date']),
        #     models.Index(fields=['subject']),
        # ]
        ordering = ['-start_date', 'course_name']
    
    def __str__(self):
        return f"{self.course_name} ({self.subject})"
    
    @property
    def enrolled_count(self):
        """Number of currently enrolled students"""
        return self.enrollments.filter(status='active').count()
    
    @property
    def is_full(self):
        """Check if course is at capacity"""
        return self.enrolled_count >= self.max_students
    
    @property
    def available_seats(self):
        """Number of available seats"""
        return max(0, self.max_students - self.enrolled_count)
    
    @property
    def total_revenue_potential(self):
        """Total potential revenue from enrolled students"""
        return self.enrolled_count * self.fee_per_month * self.duration_months


class CourseInstructor(models.Model):
    """Many-to-many relationship between Course and Instructor with additional fields"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_instructors'
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name='instructor_courses'
    )
    
    # Assignment details
    assigned_date = models.DateField(auto_now_add=True)
    is_primary = models.BooleanField(
        default=True,
        help_text="Is this the primary instructor for the course?"
    )
    
    # Hours tracking
    hours_taught = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Total hours taught in this course"
    )
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('course', 'instructor')
        indexes = [
            models.Index(fields=['course', 'instructor']),
        ]
        ordering = ['-is_primary', 'assigned_date']
    
    def __str__(self):
        primary = "Primary" if self.is_primary else "Assistant"
        return f"{self.instructor.full_name} - {self.course.course_name} ({primary})"


class Enrollment(models.Model):
    """Student enrollment in courses"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('suspended', 'Suspended'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Enrollment details
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Completion
    final_grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Final grade (0-100)"
    )
    completion_date = models.DateField(blank=True, null=True)
    
    # Additional
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'course')
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
            models.Index(fields=['enrollment_date']),
        ]
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.course.course_name}"
    
    @property
    def attendance_rate(self):
        """Calculate attendance rate percentage"""
        from apps.attendance.models import Attendance
        total = Attendance.objects.filter(
            enrollment=self
        ).count()
        
        if total == 0:
            return None
        
        present = Attendance.objects.filter(
            enrollment=self,
            status='present'
        ).count()
        
        return (present / total) * 100
    
    @property
    def total_paid(self):
        """Total amount paid for this enrollment"""
        from apps.payments.models import Payment
        return Payment.objects.filter(
            enrollment=self,
            status='paid'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    
    @property
    def total_due(self):
        """Total amount due for this enrollment"""
        return self.course.fee_per_month * self.course.duration_months
    
    @property
    def balance(self):
        """Remaining balance"""
        return self.total_due - self.total_paid