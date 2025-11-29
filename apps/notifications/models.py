# apps/notifications/models.py
from django.db import models
from apps.accounts.models import User
from datetime import datetime


class Notification(models.Model):
    """Notification model for system messages"""
    NOTIFICATION_TYPE_CHOICES = [
        ('payment_reminder', 'Payment Reminder'),
        ('payment_received', 'Payment Received'),
        ('enrollment_confirmed', 'Enrollment Confirmed'),
        ('attendance_alert', 'Attendance Alert'),
        ('course_update', 'Course Update'),
        ('financial_report', 'Financial Report'),
        ('system_alert', 'System Alert'),
        ('general', 'General'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
    ]
    
    # Notification details
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    
    # Recipient
    recipient_type = models.CharField(
        max_length=20,
        choices=[('student', 'Student'), ('parent', 'Parent'), ('instructor', 'Instructor'), 
                 ('member', 'Member'), ('admin', 'Admin')],
        help_text="Type of recipient"
    )
    recipient_id = models.IntegerField(help_text="ID of the recipient")
    recipient_contact = models.CharField(max_length=200, help_text="Email or phone number")
    
    # Content
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Scheduling
    scheduled_time = models.DateTimeField(blank=True, null=True)
    sent_time = models.DateTimeField(blank=True, null=True)
    
    # Tracking
    delivery_attempts = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    
    # Related objects
    related_model = models.CharField(max_length=50, blank=True, null=True)
    related_id = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['recipient_type', 'recipient_id']),
            models.Index(fields=['status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['scheduled_time']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} to {self.recipient_contact} - {self.status}"
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.status = 'sent'
        self.sent_time = datetime.now()
        self.save()
    
    def mark_as_failed(self, error):
        """Mark notification as failed"""
        self.status = 'failed'
        self.error_message = str(error)
        self.delivery_attempts += 1
        self.save()


class NotificationTemplate(models.Model):
    """Template for notifications"""
    # Template details
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(
        max_length=30,
        choices=Notification.NOTIFICATION_TYPE_CHOICES
    )
    channel = models.CharField(max_length=20, choices=Notification.CHANNEL_CHOICES)
    
    # Content templates
    subject_template = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Subject template with variables like {student_name}"
    )
    message_template = models.TextField(
        help_text="Message template with variables like {amount}, {due_date}, etc."
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    variables_help = models.TextField(
        blank=True,
        null=True,
        help_text="Documentation of available variables"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['notification_type', 'channel']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['notification_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.notification_type} - {self.channel})"
    
    def render(self, context):
        """Render template with provided context"""
        subject = self.subject_template.format(**context) if self.subject_template else None
        message = self.message_template.format(**context)
        return subject, message


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Email preferences
    email_payment_reminders = models.BooleanField(default=True)
    email_enrollment_updates = models.BooleanField(default=True)
    email_attendance_alerts = models.BooleanField(default=True)
    email_financial_reports = models.BooleanField(default=True)
    email_system_alerts = models.BooleanField(default=True)
    
    # SMS preferences
    sms_payment_reminders = models.BooleanField(default=True)
    sms_enrollment_updates = models.BooleanField(default=False)
    sms_attendance_alerts = models.BooleanField(default=True)
    sms_financial_reports = models.BooleanField(default=False)
    sms_system_alerts = models.BooleanField(default=True)
    
    # Push notification preferences
    push_payment_reminders = models.BooleanField(default=True)
    push_enrollment_updates = models.BooleanField(default=True)
    push_attendance_alerts = models.BooleanField(default=True)
    push_financial_reports = models.BooleanField(default=False)
    push_system_alerts = models.BooleanField(default=True)
    
    # Contact information
    preferred_email = models.EmailField(blank=True, null=True)
    preferred_phone = models.CharField(max_length=17, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
    
    def allows_notification(self, notification_type, channel):
        """Check if user allows this type of notification on this channel"""
        pref_key = f"{channel}_{notification_type}"
        return getattr(self, pref_key, True)


class NotificationLog(models.Model):
    """Log of sent notifications for analytics"""
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    # Event details
    event_type = models.CharField(
        max_length=20,
        choices=[
            ('created', 'Created'),
            ('scheduled', 'Scheduled'),
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('opened', 'Opened'),
            ('clicked', 'Clicked'),
            ('failed', 'Failed'),
            ('bounced', 'Bounced'),
        ]
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['notification', 'event_type']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.notification.id} - {self.event_type} at {self.timestamp}"