# apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password"""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as username"""
    
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('instructor', 'Instructor'),
        ('staff', 'Staff'),
        ('member', 'Member'),
    ]
    
    # Remove username, use email instead
    username = None
    email = models.EmailField(_('email address'), unique=True, db_index = True)
    
    # Additional fields
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='staff', db_index = True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    
    # Profile
    full_name = models.CharField(max_length=200, blank=True, null=True)
    avatar = models.CharField(max_length=500, blank=True, null=True, help_text="URL or path to avatar image")
    bio = models.TextField(blank=True, null=True)
    
    # Linked entities (optional - links to other models)
    instructor_id = models.IntegerField(blank=True, null=True, help_text="Linked instructor ID")
    member_id = models.IntegerField(blank=True, null=True, help_text="Linked member ID")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is already required by default
    
    objects = CustomUserManager()
    
    class Meta:
        # db_index = True
        # indexes = [
        #     models.Index(fields=['email']),
        #     models.Index(fields=['user_type']),
        #     models.Index(fields=['is_active']),
        # ]
        ordering = ['-created_at']
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name or email"""
        return self.full_name or self.email
    
    def get_short_name(self):
        """Return the email"""
        return self.email
    
    @property
    def is_admin(self):
        """Check if user is an admin"""
        return self.user_type == 'admin' or self.is_superuser
    
    @property
    def is_manager(self):
        """Check if user is a manager"""
        return self.user_type in ['admin', 'manager'] or self.is_superuser
    
    @property
    def is_instructor_user(self):
        """Check if user is an instructor"""
        return self.user_type == 'instructor'
    
    @property
    def linked_instructor(self):
        """Get linked instructor object"""
        if self.instructor_id:
            from apps.instructors.models import Instructor
            try:
                return Instructor.objects.get(id=self.instructor_id)
            except Instructor.DoesNotExist:
                return None
        return None
    
    @property
    def linked_member(self):
        """Get linked member object"""
        if self.member_id:
            from apps.members.models import Member
            try:
                return Member.objects.get(id=self.member_id)
            except Member.DoesNotExist:
                return None
        return None


class UserProfile(models.Model):
    """Extended user profile with additional settings"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Preferences
    language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('fr', 'Français'),
            ('ar', 'العربية'),
        ],
        default='fr'
    )
    timezone = models.CharField(max_length=50, default='Africa/Casablanca')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Dashboard preferences
    dashboard_layout = models.JSONField(
        default=dict,
        blank=True,
        help_text="User's dashboard layout configuration"
    )
    
    # Additional info
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)
    emergency_phone = models.CharField(max_length=17, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self):
        return f"Profile of {self.user.email}"


class UserActivity(models.Model):
    """Track user activity for audit purposes"""
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    
    # Activity details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    
    # Target object (what was affected)
    target_model = models.CharField(max_length=100, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    
    # Request information
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    
    # Additional data
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional activity metadata"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['target_model', 'target_id']),
        ]
        ordering = ['-timestamp']
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.timestamp}"


class LoginAttempt(models.Model):
    """Track login attempts for security"""
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    ]
    
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    failure_reason = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['status', 'timestamp']),
        ]
        ordering = ['-timestamp']
        verbose_name = _('login attempt')
        verbose_name_plural = _('login attempts')
    
    def __str__(self):
        return f"{self.email} - {self.status} - {self.timestamp}"
    
    @classmethod
    def is_blocked(cls, email, minutes=30, max_attempts=5):
        """Check if email is blocked due to too many failed attempts"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        recent_failures = cls.objects.filter(
            email=email,
            status='failed',
            timestamp__gte=cutoff_time
        ).count()
        
        return recent_failures >= max_attempts


class Permission(models.Model):
    """Custom permissions for fine-grained access control"""
    
    PERMISSION_CATEGORIES = [
        ('students', 'Students'),
        ('instructors', 'Instructors'),
        ('courses', 'Courses'),
        ('payments', 'Payments'),
        ('financials', 'Financials'),
        ('reports', 'Reports'),
        ('members', 'Members'),
        ('settings', 'Settings'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=PERMISSION_CATEGORIES)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
    
    def __str__(self):
        return f"{self.category} - {self.name}"


class Role(models.Model):
    """Role-based access control"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField(
        Permission,
        related_name='roles',
        blank=True
    )
    
    # Role settings
    is_system_role = models.BooleanField(
        default=False,
        help_text="System roles cannot be deleted"
    )
    is_active = models.BooleanField(default=True, db_index = True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('role')
        verbose_name_plural = _('roles')
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """Assign roles to users"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    
    # Assignment details
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='role_assignments_made'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    # Expiry (optional)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'role')
        indexes = [
            models.Index(fields=['user', 'role']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = _('user role')
        verbose_name_plural = _('user roles')
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
    
    @property
    def is_expired(self):
        """Check if role assignment has expired"""
        from django.utils import timezone
        if self.expires_at:
            return self.expires_at < timezone.now()
        return False
    
    @property
    def is_active(self):
        """Check if role assignment is active"""
        return not self.is_expired and self.role.is_active


class APIKey(models.Model):
    """API keys for external integrations"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    
    # Key details
    name = models.CharField(max_length=100, help_text="Descriptive name for this API key")
    key = models.CharField(max_length=100, unique=True)
    prefix = models.CharField(max_length=10)
    
    # Permissions
    scopes = models.JSONField(
        default=list,
        help_text="List of allowed API scopes/permissions"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Usage tracking
    last_used_at = models.DateTimeField(blank=True, null=True)
    request_count = models.PositiveIntegerField(default=0)
    
    # Expiry
    expires_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['prefix']),
            models.Index(fields=['user', 'is_active']),
        ]
        ordering = ['-created_at']
        verbose_name = _('API key')
        verbose_name_plural = _('API keys')
    
    def __str__(self):
        return f"{self.name} ({self.prefix}***)"
    
    @property
    def is_expired(self):
        """Check if API key has expired"""
        from django.utils import timezone
        if self.expires_at:
            return self.expires_at < timezone.now()
        return False
    
    @property
    def is_valid(self):
        """Check if API key is valid and active"""
        return self.is_active and not self.is_expired
    
    def increment_usage(self):
        """Increment usage counter"""
        from django.utils import timezone
        self.request_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['request_count', 'last_used_at'])