# apps/documents/models.py
from django.db import models
from apps.accounts.models import User
from datetime import date


class Document(models.Model):
    """Document model for file management"""
    DOCUMENT_TYPE_CHOICES = [
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('certificate', 'Certificate'),
        ('report', 'Report'),
        ('contract', 'Contract'),
        ('id_document', 'ID Document'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('finalized', 'Finalized'),
        ('sent', 'Sent'),
        ('archived', 'Archived'),
    ]
    
    # Document details
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    document_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # File information
    file_path = models.CharField(max_length=500)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Related entities
    related_model = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Model name (e.g., 'student', 'instructor')"
    )
    related_id = models.IntegerField(
        blank=True,
        null=True,
        help_text="ID of the related object"
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    document_date = models.DateField(default=date.today)
    
    # Upload information
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents'
    )
    
    # Additional
    description = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['document_number']),
            models.Index(fields=['related_model', 'related_id']),
            models.Index(fields=['status']),
            models.Index(fields=['document_date']),
        ]
        ordering = ['-document_date', '-created_at']
    
    def __str__(self):
        return f"{self.document_type} - {self.title}"
    
    @property
    def file_size_mb(self):
        """File size in MB"""
        return round(self.file_size / (1024 * 1024), 2)


class DocumentTemplate(models.Model):
    """Template for generating documents"""
    TEMPLATE_TYPE_CHOICES = [
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('certificate', 'Certificate'),
        ('report', 'Report'),
        ('contract', 'Contract'),
        ('letter', 'Letter'),
    ]
    
    # Template details
    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    
    # Template content
    html_template = models.TextField(
        help_text="HTML template with variables"
    )
    css_styles = models.TextField(
        blank=True,
        null=True,
        help_text="CSS styles for the template"
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Is this the default template for this type?"
    )
    
    # Page settings
    page_size = models.CharField(
        max_length=10,
        default='A4',
        help_text="Page size (A4, Letter, etc.)"
    )
    orientation = models.CharField(
        max_length=10,
        choices=[('portrait', 'Portrait'), ('landscape', 'Landscape')],
        default='portrait'
    )
    
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
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['is_default']),
        ]
        ordering = ['template_type', 'name']
    
    def __str__(self):
        default = " (Default)" if self.is_default else ""
        return f"{self.name}{default}"


class StudentDocument(models.Model):
    """Documents specific to students"""
    DOCUMENT_TYPE_CHOICES = [
        ('birth_certificate', 'Birth Certificate'),
        ('id_card', 'ID Card'),
        ('photo', 'Photo'),
        ('medical_certificate', 'Medical Certificate'),
        ('enrollment_form', 'Enrollment Form'),
        ('consent_form', 'Consent Form'),
        ('transcript', 'Academic Transcript'),
        ('other', 'Other'),
    ]
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    # Document details
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_student_documents'
    )
    verification_date = models.DateField(blank=True, null=True)
    
    # Expiry (for time-sensitive documents)
    expiry_date = models.DateField(blank=True, null=True)
    
    # Upload info
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_student_documents'
    )
    upload_date = models.DateField(default=date.today)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['student', 'document_type']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['expiry_date']),
        ]
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.document_type}"
    
    @property
    def is_expired(self):
        """Check if document has expired"""
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False


class InstructorDocument(models.Model):
    """Documents specific to instructors"""
    DOCUMENT_TYPE_CHOICES = [
        ('id_card', 'ID Card'),
        ('resume', 'Resume/CV'),
        ('degree', 'Degree Certificate'),
        ('certificate', 'Professional Certificate'),
        ('contract', 'Employment Contract'),
        ('background_check', 'Background Check'),
        ('tax_form', 'Tax Form'),
        ('bank_info', 'Bank Information'),
        ('other', 'Other'),
    ]
    
    instructor = models.ForeignKey(
        'instructors.Instructor',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    # Document details
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_instructor_documents'
    )
    verification_date = models.DateField(blank=True, null=True)
    
    # Expiry
    expiry_date = models.DateField(blank=True, null=True)
    
    # Upload info
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_instructor_documents'
    )
    upload_date = models.DateField(default=date.today)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['instructor', 'document_type']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['expiry_date']),
        ]
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.instructor.full_name} - {self.document_type}"
    
    @property
    def is_expired(self):
        """Check if document has expired"""
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False