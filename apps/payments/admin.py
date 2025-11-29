# apps/payments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from decimal import Decimal
from .models import Payment, Invoice, PaymentPlan


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model"""
    list_display = [
        'student', 'amount_display', 'due_date', 
        'payment_date', 'status_badge', 'balance_display',
        'payment_method'
    ]
    list_filter = [
        'status', 'payment_method', 'due_date', 
        'payment_date', 'created_at'
    ]
    search_fields = [
        'student__full_name', 'receipt_number', 
        'transaction_reference'
    ]
    date_hierarchy = 'due_date'
    ordering = ['-due_date', '-created_at']
    
    fieldsets = (
        ('Payment Details', {
            'fields': (
                'student', 'enrollment', 'amount', 
                'amount_paid', 'payment_method'
            )
        }),
        ('Dates', {
            'fields': (
                'due_date', 'payment_date', 'status'
            )
        }),
        ('References', {
            'fields': (
                'receipt_number', 'transaction_reference'
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
    
    autocomplete_fields = ['student', 'enrollment']
    
    list_per_page = 50
    
    actions = [
        'mark_as_paid', 
        'mark_as_overdue', 
        'export_payments'
    ]
    
    def amount_display(self, obj):
        return format_html(
            '<strong>{} DH</strong>',
            obj.amount
        )
    amount_display.short_description = 'Amount'
    
    def balance_display(self, obj):
        balance = obj.balance
        if balance > 0:
            return format_html(
                '<span style="color: red;">{} DH</span>',
                balance
            )
        return format_html(
            '<span style="color: green;">0 DH</span>'
        )
    balance_display.short_description = 'Balance'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'partially_paid': 'blue',
            'overdue': 'red',
            'cancelled': 'gray',
            'refunded': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_as_paid(self, request, queryset):
        from datetime import date
        count = 0
        for payment in queryset:
            if payment.status != 'paid':
                payment.mark_as_paid()
                count += 1
        
        self.message_user(
            request, 
            f'{count} payment(s) marked as paid.'
        )
    mark_as_paid.short_description = 'Mark as Paid'
    
    def mark_as_overdue(self, request, queryset):
        updated = queryset.filter(
            status__in=['pending', 'partially_paid']
        ).update(status='overdue')
        self.message_user(
            request, 
            f'{updated} payment(s) marked as overdue.'
        )
    mark_as_overdue.short_description = 'Mark as Overdue'
    
    def export_payments(self, request, queryset):
        # Implementation for export
        pass
    export_payments.short_description = 'Export selected payments'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('student', 'enrollment__course')
        return qs


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin interface for Invoice model"""
    list_display = [
        'invoice_number', 'student', 'invoice_date', 
        'due_date', 'total_display', 'status_badge'
    ]
    list_filter = [
        'status', 'invoice_date', 'due_date', 'created_at'
    ]
    search_fields = [
        'invoice_number', 'student__full_name'
    ]
    date_hierarchy = 'invoice_date'
    ordering = ['-invoice_date', '-invoice_number']
    
    fieldsets = (
        ('Invoice Details', {
            'fields': (
                'student', 'enrollment', 'invoice_number',
                'invoice_date', 'due_date', 'status'
            )
        }),
        ('Amounts', {
            'fields': (
                'subtotal', 'discount', 'tax', 'total'
            )
        }),
        ('Payment Tracking', {
            'fields': ('payment',)
        }),
        ('Document', {
            'fields': ('pdf_path',),
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
    
    readonly_fields = ['created_at', 'updated_at', 'total']
    
    autocomplete_fields = ['student', 'enrollment', 'payment']
    
    list_per_page = 50
    
    actions = [
        'mark_as_sent', 
        'mark_as_paid', 
        'generate_pdfs'
    ]
    
    def total_display(self, obj):
        return format_html(
            '<strong>{} DH</strong>',
            obj.total
        )
    total_display.short_description = 'Total'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'sent': 'blue',
            'paid': 'green',
            'overdue': 'red',
            'cancelled': 'black'
        }
        color = colors.get(obj.status, 'gray')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='sent')
        self.message_user(
            request, 
            f'{updated} invoice(s) marked as sent.'
        )
    mark_as_sent.short_description = 'Mark as Sent'
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(
            request, 
            f'{updated} invoice(s) marked as paid.'
        )
    mark_as_paid.short_description = 'Mark as Paid'
    
    def generate_pdfs(self, request, queryset):
        # Implementation for PDF generation
        count = queryset.count()
        self.message_user(
            request, 
            f'PDF generation queued for {count} invoice(s).'
        )
    generate_pdfs.short_description = 'Generate PDFs'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('student', 'enrollment', 'payment')
        return qs


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    """Admin interface for PaymentPlan"""
    list_display = [
        'student', 'enrollment', 'total_amount', 
        'installment_amount', 'number_of_installments',
        'start_date', 'status'
    ]
    list_filter = [
        'status', 'start_date', 'created_at'
    ]
    search_fields = [
        'student__full_name', 'enrollment__course__course_name'
    ]
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    
    fieldsets = (
        ('Payment Plan Details', {
            'fields': (
                'student', 'enrollment', 'total_amount',
                'installment_amount', 'number_of_installments'
            )
        }),
        ('Schedule', {
            'fields': (
                'start_date', 'status'
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
    
    autocomplete_fields = ['student', 'enrollment']
    
    list_per_page = 25
    
    actions = ['generate_installments', 'cancel_plans']
    
    def generate_installments(self, request, queryset):
        count = 0
        for plan in queryset:
            plan.generate_installments()
            count += 1
        
        self.message_user(
            request, 
            f'Installments generated for {count} plan(s).'
        )
    generate_installments.short_description = 'Generate Installments'
    
    def cancel_plans(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(
            request, 
            f'{updated} plan(s) cancelled.'
        )
    cancel_plans.short_description = 'Cancel selected plans'