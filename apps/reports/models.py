# apps/reports/models.py
from django.db import models
from apps.accounts.models import User
from datetime import date


class Report(models.Model):
    """Report model for generated reports"""
    REPORT_TYPE_CHOICES = [
        ('financial', 'Financial Report'),
        ('attendance', 'Attendance Report'),
        ('enrollment', 'Enrollment Report'),
        ('student_performance', 'Student Performance Report'),
        ('instructor_performance', 'Instructor Performance Report'),
        ('revenue', 'Revenue Report'),
        ('expense', 'Expense Report'),
        ('profit_distribution', 'Profit Distribution Report'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('html', 'HTML'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Report details
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Report parameters
    parameters = models.JSONField(
        default=dict,
        help_text="Report parameters (date ranges, filters, etc.)"
    )
    
    # Period
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    # Output
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Generation info
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports'
    )
    generation_started_at = models.DateTimeField(blank=True, null=True)
    generation_completed_at = models.DateTimeField(blank=True, null=True)
    
    # Access tracking
    download_count = models.PositiveIntegerField(default=0)
    last_downloaded_at = models.DateTimeField(blank=True, null=True)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly'),
        ],
        blank=True,
        null=True
    )
    next_generation_date = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['status']),
            models.Index(fields=['generated_by']),
            models.Index(fields=['is_scheduled', 'next_generation_date']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.report_type})"
    
    @property
    def file_size_mb(self):
        """File size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def generation_time(self):
        """Time taken to generate report"""
        if self.generation_started_at and self.generation_completed_at:
            delta = self.generation_completed_at - self.generation_started_at
            return delta.total_seconds()
        return None


class ReportTemplate(models.Model):
    """Template for reports"""
    # Template details
    name = models.CharField(max_length=100, unique=True)
    report_type = models.CharField(max_length=30, choices=Report.REPORT_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    # Template configuration
    default_parameters = models.JSONField(
        default=dict,
        help_text="Default parameters for this report type"
    )
    
    # Layout
    template_content = models.TextField(
        blank=True,
        null=True,
        help_text="HTML/template content for the report"
    )
    css_styles = models.TextField(blank=True, null=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Metadata
    required_permissions = models.JSONField(
        default=list,
        help_text="Required permissions to generate this report"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['report_type', 'is_active']),
            models.Index(fields=['is_default']),
        ]
        ordering = ['report_type', 'name']
    
    def __str__(self):
        default = " (Default)" if self.is_default else ""
        return f"{self.name}{default}"


class ReportSchedule(models.Model):
    """Scheduled report generation"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Schedule details
    name = models.CharField(max_length=200)
    report_template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    # Schedule configuration
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    parameters = models.JSONField(default=dict)
    
    # Recipients
    recipients = models.JSONField(
        default=list,
        help_text="List of email addresses to send report to"
    )
    
    # Timing
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(blank=True, null=True)
    next_run_date = models.DateField()
    last_run_date = models.DateField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Tracking
    total_runs = models.PositiveIntegerField(default=0)
    successful_runs = models.PositiveIntegerField(default=0)
    failed_runs = models.PositiveIntegerField(default=0)
    
    # Created by
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_report_schedules'
    )
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'next_run_date']),
            models.Index(fields=['frequency']),
        ]
        ordering = ['next_run_date']
    
    def __str__(self):
        return f"{self.name} ({self.frequency})"
    
    @property
    def success_rate(self):
        """Success rate percentage"""
        if self.total_runs > 0:
            return (self.successful_runs / self.total_runs) * 100
        return 0


class ReportShare(models.Model):
    """Track report sharing"""
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    
    # Share details
    shared_with_email = models.EmailField()
    shared_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='shared_reports'
    )
    
    # Access control
    access_token = models.CharField(max_length=100, unique=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Tracking
    access_count = models.PositiveIntegerField(default=0)
    last_accessed_at = models.DateTimeField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['report', 'is_active']),
            models.Index(fields=['access_token']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report.title} shared with {self.shared_with_email}"
    
    @property
    def is_expired(self):
        """Check if share has expired"""
        from django.utils import timezone
        if self.expires_at:
            return self.expires_at < timezone.now()
        return False
    
    @property
    def is_accessible(self):
        """Check if share is accessible"""
        return self.is_active and not self.is_expired