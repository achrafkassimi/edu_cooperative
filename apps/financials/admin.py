# apps/financials/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import (
    InstructorPayment, MonthlyFinancial, 
    MemberDistribution, Expense, BudgetAllocation
)


@admin.register(InstructorPayment)
class InstructorPaymentAdmin(admin.ModelAdmin):
    """Admin interface for InstructorPayment"""
    list_display = [
        'instructor', 'period_month', 'total_hours',
        'gross_amount', 'net_amount', 'status_badge',
        'payment_date'
    ]
    list_filter = [
        'status', 'period_month', 'payment_date', 'created_at'
    ]
    search_fields = [
        'instructor__full_name', 'transaction_reference'
    ]
    date_hierarchy = 'period_month'
    ordering = ['-period_month', 'instructor__full_name']
    
    fieldsets = (
        ('Payment Details', {
            'fields': (
                'instructor', 'period_month'
            )
        }),
        ('Calculation', {
            'fields': (
                'total_hours', 'hourly_rate', 'gross_amount',
                'tax_amount', 'net_amount'
            )
        }),
        ('Payment Information', {
            'fields': (
                'status', 'payment_date', 'payment_method',
                'transaction_reference'
            )
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
    
    autocomplete_fields = ['instructor']
    
    list_per_page = 50
    
    actions = [
        'approve_payments', 
        'mark_as_paid', 
        'calculate_amounts'
    ]
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'blue',
            'paid': 'green',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_payments(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='approved')
        self.message_user(
            request, 
            f'{updated} payment(s) approved.'
        )
    approve_payments.short_description = 'Approve selected payments'
    
    def mark_as_paid(self, request, queryset):
        from datetime import date
        updated = queryset.filter(
            status='approved'
        ).update(status='paid', payment_date=date.today())
        self.message_user(
            request, 
            f'{updated} payment(s) marked as paid.'
        )
    mark_as_paid.short_description = 'Mark as Paid'
    
    def calculate_amounts(self, request, queryset):
        count = 0
        for payment in queryset:
            payment.calculate_amounts()
            count += 1
        
        self.message_user(
            request, 
            f'Amounts calculated for {count} payment(s).'
        )
    calculate_amounts.short_description = 'Calculate Amounts'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('instructor')
        return qs


@admin.register(MonthlyFinancial)
class MonthlyFinancialAdmin(admin.ModelAdmin):
    """Admin interface for MonthlyFinancial"""
    list_display = [
        'period_month', 'total_revenue', 'total_expenses',
        'gross_profit', 'distributable_profit', 
        'is_finalized', 'finalized_date'
    ]
    list_filter = [
        'is_finalized', 'period_month', 'finalized_date'
    ]
    search_fields = ['notes']
    date_hierarchy = 'period_month'
    ordering = ['-period_month']
    
    fieldsets = (
        ('Period', {
            'fields': ('period_month',)
        }),
        ('Revenue', {
            'fields': ('total_revenue',)
        }),
        ('Expenses', {
            'fields': (
                'instructor_payments', 'operational_expenses',
                'other_expenses', 'total_expenses'
            )
        }),
        ('Profit', {
            'fields': (
                'gross_profit', 'retained_earnings',
                'distributable_profit'
            )
        }),
        ('Status', {
            'fields': (
                'is_finalized', 'finalized_date'
            )
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
    
    readonly_fields = ['total_expenses', 'created_at', 'updated_at']
    
    list_per_page = 25
    
    actions = [
        'finalize_periods', 
        'recalculate_totals'
    ]
    
    def finalize_periods(self, request, queryset):
        from datetime import date
        updated = queryset.filter(
            is_finalized=False
        ).update(is_finalized=True, finalized_date=date.today())
        self.message_user(
            request, 
            f'{updated} period(s) finalized.'
        )
    finalize_periods.short_description = 'Finalize selected periods'
    
    def recalculate_totals(self, request, queryset):
        count = 0
        for financial in queryset:
            financial.calculate_totals()
            count += 1
        
        self.message_user(
            request, 
            f'Totals recalculated for {count} period(s).'
        )
    recalculate_totals.short_description = 'Recalculate Totals'


@admin.register(MemberDistribution)
class MemberDistributionAdmin(admin.ModelAdmin):
    """Admin interface for MemberDistribution"""
    list_display = [
        'member', 'period', 'share_percentage',
        'amount', 'status_badge', 'is_public_employee',
        'payment_date'
    ]
    list_filter = [
        'status', 'is_public_employee', 
        'monthly_financial__period_month', 'payment_date'
    ]
    search_fields = [
        'member__full_name', 'member__membership_number',
        'transaction_reference'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-monthly_financial__period_month', 'member__full_name']
    
    fieldsets = (
        ('Distribution Details', {
            'fields': (
                'member', 'monthly_financial', 
                'share_percentage', 'amount'
            )
        }),
        ('Payment Information', {
            'fields': (
                'status', 'payment_date', 'payment_method',
                'transaction_reference'
            )
        }),
        ('Restrictions', {
            'fields': ('is_public_employee',)
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
    
    readonly_fields = ['is_public_employee', 'created_at', 'updated_at']
    
    autocomplete_fields = ['member', 'monthly_financial']
    
    list_per_page = 50
    
    def period(self, obj):
        return obj.monthly_financial.period_month.strftime('%B %Y')
    period.short_description = 'Period'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'blue',
            'paid': 'green',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = [
        'approve_distributions', 
        'mark_as_paid'
    ]
    
    def approve_distributions(self, request, queryset):
        # Only approve for non-public employees
        updated = queryset.filter(
            status='pending',
            is_public_employee=False
        ).update(status='approved')
        self.message_user(
            request, 
            f'{updated} distribution(s) approved.'
        )
    approve_distributions.short_description = 'Approve selected distributions'
    
    def mark_as_paid(self, request, queryset):
        from datetime import date
        updated = queryset.filter(
            status='approved'
        ).update(status='paid', payment_date=date.today())
        self.message_user(
            request, 
            f'{updated} distribution(s) marked as paid.'
        )
    mark_as_paid.short_description = 'Mark as Paid'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('member', 'monthly_financial')
        return qs


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Admin interface for Expense"""
    list_display = [
        'expense_date', 'category', 'description',
        'amount', 'status_badge', 'payment_date',
        'receipt_number'
    ]
    list_filter = [
        'category', 'status', 'expense_date', 
        'payment_date', 'period_month'
    ]
    search_fields = [
        'description', 'receipt_number', 'approved_by'
    ]
    date_hierarchy = 'expense_date'
    ordering = ['-expense_date', '-created_at']
    
    fieldsets = (
        ('Expense Details', {
            'fields': (
                'category', 'description', 'amount',
                'expense_date', 'period_month'
            )
        }),
        ('Payment Information', {
            'fields': (
                'status', 'payment_date', 'payment_method'
            )
        }),
        ('Documentation', {
            'fields': (
                'receipt_number', 'receipt_image'
            )
        }),
        ('Approval', {
            'fields': (
                'approved_by', 'approval_date'
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
    
    list_per_page = 50
    
    actions = [
        'approve_expenses', 
        'mark_as_paid', 
        'reject_expenses'
    ]
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'blue',
            'paid': 'green',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_expenses(self, request, queryset):
        from datetime import date
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user.full_name or request.user.email,
            approval_date=date.today()
        )
        self.message_user(
            request, 
            f'{updated} expense(s) approved.'
        )
    approve_expenses.short_description = 'Approve selected expenses'
    
    def mark_as_paid(self, request, queryset):
        from datetime import date
        updated = queryset.filter(
            status='approved'
        ).update(status='paid', payment_date=date.today())
        self.message_user(
            request, 
            f'{updated} expense(s) marked as paid.'
        )
    mark_as_paid.short_description = 'Mark as Paid'
    
    def reject_expenses(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(
            request, 
            f'{updated} expense(s) rejected.'
        )
    reject_expenses.short_description = 'Reject selected expenses'


@admin.register(BudgetAllocation)
class BudgetAllocationAdmin(admin.ModelAdmin):
    """Admin interface for BudgetAllocation"""
    list_display = [
        'period_month', 'category', 'allocated_amount',
        'spent_display', 'remaining_display', 
        'utilization_display'
    ]
    list_filter = [
        'category', 'period_month', 'created_at'
    ]
    search_fields = ['category', 'notes']
    date_hierarchy = 'period_month'
    ordering = ['-period_month', 'category']
    
    fieldsets = (
        ('Budget Details', {
            'fields': (
                'period_month', 'category', 'allocated_amount'
            )
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
    
    list_per_page = 50
    
    def spent_display(self, obj):
        spent = obj.spent_amount
        return format_html(
            '<strong>{} DH</strong>',
            spent
        )
    spent_display.short_description = 'Spent'
    
    def remaining_display(self, obj):
        remaining = obj.remaining_budget
        color = 'green' if remaining > 0 else 'red'
        return format_html(
            '<span style="color: {};">{} DH</span>',
            color, remaining
        )
    remaining_display.short_description = 'Remaining'
    
    def utilization_display(self, obj):
        utilization = obj.utilization_percentage
        color = 'green' if utilization < 80 else 'orange' if utilization < 100 else 'red'
        return format_html(
            '<span style="color: {};">{}%</span>',
            color, int(utilization)
        )
    utilization_display.short_description = 'Utilization'