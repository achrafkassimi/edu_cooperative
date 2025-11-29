# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, UserProfile, UserActivity, LoginAttempt, 
    Permission, Role, UserRole, APIKey
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    list_display = [
        'email', 'full_name', 'user_type', 'is_active', 
        'is_staff', 'last_login', 'created_at'
    ]
    list_filter = [
        'user_type', 'is_active', 'is_staff', 
        'is_superuser', 'created_at'
    ]
    search_fields = ['email', 'full_name', 'phone']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'phone', 'avatar', 'bio')
        }),
        ('User Type & Permissions', {
            'fields': (
                'user_type', 'is_active', 'is_staff', 
                'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Linked Entities', {
            'fields': ('instructor_id', 'member_id'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'full_name', 
                'user_type', 'is_active', 'is_staff'
            ),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile"""
    list_display = [
        'user', 'language', 'timezone', 
        'email_notifications', 'sms_notifications', 'updated_at'
    ]
    list_filter = [
        'language', 'timezone', 'email_notifications', 
        'sms_notifications', 'push_notifications'
    ]
    search_fields = ['user__email', 'user__full_name']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Preferences', {
            'fields': ('language', 'timezone')
        }),
        ('Notifications', {
            'fields': (
                'email_notifications', 'sms_notifications', 
                'push_notifications'
            )
        }),
        ('Dashboard', {
            'fields': ('dashboard_layout',),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': (
                'date_of_birth', 'address', 
                'emergency_contact', 'emergency_phone'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin interface for UserActivity"""
    list_display = [
        'user', 'action', 'description', 'target_model', 
        'target_id', 'timestamp'
    ]
    list_filter = ['action', 'timestamp', 'target_model']
    search_fields = ['user__email', 'description', 'target_model']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    readonly_fields = [
        'user', 'action', 'description', 'target_model', 
        'target_id', 'ip_address', 'user_agent', 'metadata', 'timestamp'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Admin interface for LoginAttempt"""
    list_display = [
        'email', 'status', 'ip_address', 
        'failure_reason', 'timestamp'
    ]
    list_filter = ['status', 'timestamp']
    search_fields = ['email', 'ip_address']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    readonly_fields = [
        'email', 'status', 'ip_address', 
        'user_agent', 'failure_reason', 'timestamp'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin interface for Permission"""
    list_display = ['name', 'codename', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'codename', 'description']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Permission Details', {
            'fields': ('name', 'codename', 'category', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role"""
    list_display = [
        'name', 'is_system_role', 'is_active', 
        'permissions_count', 'created_at'
    ]
    list_filter = ['is_system_role', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']
    
    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'description')
        }),
        ('Permissions', {
            'fields': ('permissions',)
        }),
        ('Settings', {
            'fields': ('is_system_role', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def permissions_count(self, obj):
        return obj.permissions.count()
    permissions_count.short_description = 'Permissions'
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_system_role:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin interface for UserRole"""
    list_display = [
        'user', 'role', 'assigned_by', 
        'assigned_at', 'expires_at', 'is_active_status'
    ]
    list_filter = ['role', 'assigned_at', 'expires_at']
    search_fields = ['user__email', 'role__name']
    date_hierarchy = 'assigned_at'
    
    fieldsets = (
        ('Assignment', {
            'fields': ('user', 'role')
        }),
        ('Details', {
            'fields': ('assigned_by', 'assigned_at', 'expires_at', 'notes')
        }),
    )
    
    readonly_fields = ['assigned_at']
    
    def is_active_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Inactive/Expired</span>'
        )
    is_active_status.short_description = 'Status'


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin interface for APIKey"""
    list_display = [
        'name', 'user', 'prefix', 'is_active', 
        'last_used_at', 'expires_at', 'request_count'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['name', 'user__email', 'prefix']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('API Key Information', {
            'fields': ('user', 'name', 'key', 'prefix')
        }),
        ('Permissions', {
            'fields': ('scopes',)
        }),
        ('Status & Expiry', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Usage Statistics', {
            'fields': ('last_used_at', 'request_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'key', 'prefix', 'last_used_at', 
        'request_count', 'created_at', 'updated_at'
    ]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return self.readonly_fields + ['user']
        return self.readonly_fields