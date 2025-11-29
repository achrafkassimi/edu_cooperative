# apps/members/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Admin interface for Member model"""
    list_display = [
        'full_name', 'membership_number', 'employment_status',
        'share_percentage', 'status', 'can_receive_profit_display',
        'join_date'
    ]
    list_filter = [
        'status', 'employment_status', 'join_date', 'created_at'
    ]
    search_fields = [
        'full_name', 'email', 'phone', 
        'membership_number'
    ]
    date_hierarchy = 'join_date'
    ordering = ['full_name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'full_name', 'email', 'phone', 'address'
            )
        }),
        ('Membership Details', {
            'fields': (
                'membership_number', 'join_date', 'status'
            )
        }),
        ('Employment Information', {
            'fields': (
                'employment_status', 'employer_name'
            )
        }),
        ('Profit Sharing', {
            'fields': ('share_percentage',)
        }),
        ('Banking Details', {
            'fields': (
                'bank_name', 'account_number'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    list_per_page = 25
    
    actions = [
        'activate_members', 
        'deactivate_members'
    ]
    
    def can_receive_profit_display(self, obj):
        if obj.can_receive_profit:
            return format_html(
                '<span style="color: green;">✓ Eligible</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Not Eligible</span>'
        )
    can_receive_profit_display.short_description = 'Profit Eligibility'
    
    def activate_members(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(
            request, 
            f'{updated} member(s) activated.'
        )
    activate_members.short_description = 'Activate selected members'
    
    def deactivate_members(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(
            request, 
            f'{updated} member(s) deactivated.'
        )
    deactivate_members.short_description = 'Deactivate selected members'