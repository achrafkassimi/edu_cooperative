# apps/students/models.py
from django.db import models
from django.core.validators import RegexValidator
from datetime import date


class Student(models.Model):
    """Student model"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
    ]
    
    EDUCATION_LEVEL_CHOICES = [
        ('primary', 'Primary School'),
        ('middle', 'Middle School'),
        ('high', 'High School'),
        ('university', 'University'),
        ('other', 'Other'),
    ]
    
    # Personal Information
    full_name = models.CharField(max_length=200, db_index = True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Parent/Guardian Information
    parent_name = models.CharField(max_length=200)
    parent_phone = models.CharField(validators=[phone_regex], max_length=17, db_index = True)
    parent_email = models.EmailField(blank=True, null=True)
    
    # Educational Information
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES)
    school_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Registration Details
    registration_date = models.DateField(default=date.today, db_index = True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index = True)
    
    # Additional Information
    medical_notes = models.TextField(blank=True, null=True, help_text="Any medical conditions or allergies")
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # db_index = True
        # indexes = [
        #     models.Index(fields=['full_name']),
        #     models.Index(fields=['parent_phone']),
        #     models.Index(fields=['status']),
        #     models.Index(fields=['registration_date']),
        # ]
        ordering = ['-registration_date', 'full_name']
    
    def __str__(self):
        return self.full_name
    
    @property
    def age(self):
        """Calculate student's age"""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def active_enrollments_count(self):
        """Count of active course enrollments"""
        return self.enrollments.filter(status='active').count()
    
    @property
    def total_payments_made(self):
        """Total amount paid by student"""
        from apps.payments.models import Payment
        return Payment.objects.filter(
            student=self,
            status='paid'
        ).aggregate(total=models.Sum('amount'))['total'] or 0