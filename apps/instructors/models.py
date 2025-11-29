# apps/instructors/models.py
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from decimal import Decimal


class Instructor(models.Model):
    """Instructor model"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
    ]
    
    # Personal Information
    full_name = models.CharField(max_length=200, db_index = True)
    email = models.EmailField(unique=True, db_index = True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17)
    address = models.TextField(blank=True, null=True)
    
    # Professional Information
    specialization = models.CharField(max_length=200, help_text="Subject area of expertise", db_index = True)
    qualifications = models.TextField(help_text="Educational qualifications and certifications")
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Employment Details
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    hire_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index = True)
    
    # Payment Information
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Hourly payment rate in DH"
    )
    
    # Tax Information
    tax_rate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Tax percentage (e.g., 10 for 10%)"
    )
    
    # Banking Details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    rib = models.CharField(max_length=24, blank=True, null=True, help_text="Relevé d'Identité Bancaire")
    
    # Additional Information
    bio = models.TextField(blank=True, null=True, help_text="Brief biography")
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # db_index = True
        # indexes = [
        #     models.Index(fields=['full_name']),
        #     models.Index(fields=['email']),
        #     models.Index(fields=['status']),
        #     models.Index(fields=['specialization']),
        # ]
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} - {self.specialization}"
    
    @property
    def active_courses_count(self):
        """Number of active courses being taught"""
        from apps.courses.models import CourseInstructor
        return CourseInstructor.objects.filter(
            instructor=self,
            course__status='active'
        ).count()
    
    @property
    def total_hours_taught(self):
        """Total hours taught across all courses"""
        from apps.courses.models import CourseInstructor
        return CourseInstructor.objects.filter(
            instructor=self
        ).aggregate(total=models.Sum('hours_taught'))['total'] or 0
    
    @property
    def total_earnings(self):
        """Total earnings from all payments"""
        from apps.financials.models import InstructorPayment
        return InstructorPayment.objects.filter(
            instructor=self,
            status='paid'
        ).aggregate(total=models.Sum('net_amount'))['total'] or Decimal('0')