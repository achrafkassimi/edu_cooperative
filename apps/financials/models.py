# apps/financials/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import date
from apps.instructors.models import Instructor
from apps.members.models import Member


class InstructorPayment(models.Model):
    """Monthly payment record for instructors"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Period
    period_month = models.DateField(help_text="First day of the payment period month")
    
    # Hours and calculation
    total_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Total hours worked in the period"
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Hourly rate at time of calculation"
    )
    
    # Amounts
    gross_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Amount before taxes"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Tax withheld"
    )
    net_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Amount after taxes"
    )
    
    # Payment details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('instructor', 'period_month')
        indexes = [
            models.Index(fields=['instructor', 'period_month']),
            models.Index(fields=['period_month']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
        ]
        ordering = ['-period_month', 'instructor__full_name']
    
    def __str__(self):
        return f"{self.instructor.full_name} - {self.period_month.strftime('%B %Y')} - {self.net_amount} DH"
    
    def calculate_amounts(self):
        """Calculate gross, tax, and net amounts"""
        self.gross_amount = self.total_hours * self.hourly_rate
        self.tax_amount = self.gross_amount * (self.instructor.tax_rate_percentage / 100)
        self.net_amount = self.gross_amount - self.tax_amount
        self.save()


class MonthlyFinancial(models.Model):
    """Monthly financial summary"""
    # Period
    period_month = models.DateField(
        unique=True,
        help_text="First day of the financial period month"
    )
    
    # Revenue
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Total student payments received"
    )
    
    # Expenses
    instructor_payments = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Total paid to instructors"
    )
    operational_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Rent, utilities, supplies, etc."
    )
    other_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Calculated fields
    total_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    gross_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )
    
    # Profit distribution
    retained_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Amount kept as reserves"
    )
    distributable_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Amount available for member distribution"
    )
    
    # Status
    is_finalized = models.BooleanField(
        default=False,
        help_text="Whether financial calculations are finalized"
    )
    finalized_date = models.DateField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['period_month']),
            models.Index(fields=['is_finalized']),
        ]
        ordering = ['-period_month']
        verbose_name = 'Monthly Financial Summary'
        verbose_name_plural = 'Monthly Financial Summaries'
    
    def __str__(self):
        return f"Financial Summary - {self.period_month.strftime('%B %Y')}"
    
    def calculate_totals(self):
        """Calculate total expenses and profit"""
        self.total_expenses = (
            self.instructor_payments +
            self.operational_expenses +
            self.other_expenses
        )
        self.gross_profit = self.total_revenue - self.total_expenses
        self.save()
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.total_revenue > 0:
            return (self.gross_profit / self.total_revenue) * 100
        return Decimal('0')


class MemberDistribution(models.Model):
    """Profit distribution to cooperative members"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='distributions'
    )
    monthly_financial = models.ForeignKey(
        MonthlyFinancial,
        on_delete=models.CASCADE,
        related_name='distributions'
    )
    
    # Distribution details
    share_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Member's share percentage at time of distribution"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Distribution amount"
    )
    
    # Payment details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Restrictions
    is_public_employee = models.BooleanField(
        default=False,
        help_text="Public employees cannot receive distributions"
    )
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('member', 'monthly_financial')
        indexes = [
            models.Index(fields=['member', 'status']),
            models.Index(fields=['monthly_financial', 'status']),
            models.Index(fields=['status']),
        ]
        ordering = ['-monthly_financial__period_month', 'member__full_name']
    
    def __str__(self):
        period = self.monthly_financial.period_month.strftime('%B %Y')
        return f"{self.member.full_name} - {period} - {self.amount} DH"
    
    def save(self, *args, **kwargs):
        # Set public employee flag from member
        self.is_public_employee = (self.member.employment_status == 'public')
        super().save(*args, **kwargs)


class Expense(models.Model):
    """Individual expense record"""
    EXPENSE_CATEGORY_CHOICES = [
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('supplies', 'Supplies'),
        ('marketing', 'Marketing'),
        ('maintenance', 'Maintenance'),
        ('insurance', 'Insurance'),
        ('salaries', 'Salaries (non-instructor)'),
        ('taxes', 'Taxes'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    
    # Expense details
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORY_CHOICES)
    description = models.CharField(max_length=500)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Date
    expense_date = models.DateField(default=date.today)
    period_month = models.DateField(help_text="Assign to which financial month")
    
    # Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    
    # Documentation
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    receipt_image = models.CharField(max_length=500, blank=True, null=True)
    
    # Approval
    approved_by = models.CharField(max_length=200, blank=True, null=True)
    approval_date = models.DateField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['expense_date']),
            models.Index(fields=['period_month']),
            models.Index(fields=['status']),
        ]
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.category} - {self.amount} DH - {self.expense_date}"


class BudgetAllocation(models.Model):
    """Monthly budget allocation by category"""
    period_month = models.DateField(help_text="Budget month")
    category = models.CharField(max_length=20, choices=Expense.EXPENSE_CATEGORY_CHOICES)
    
    allocated_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Budgeted amount for the category"
    )
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('period_month', 'category')
        indexes = [
            models.Index(fields=['period_month', 'category']),
        ]
        ordering = ['-period_month', 'category']
    
    def __str__(self):
        return f"{self.period_month.strftime('%B %Y')} - {self.category} - {self.allocated_amount} DH"
    
    @property
    def spent_amount(self):
        """Total spent in this category for the period"""
        return Expense.objects.filter(
            period_month=self.period_month,
            category=self.category,
            status='paid'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    
    @property
    def remaining_budget(self):
        """Remaining budget"""
        return self.allocated_amount - self.spent_amount
    
    @property
    def utilization_percentage(self):
        """Budget utilization percentage"""
        if self.allocated_amount > 0:
            return (self.spent_amount / self.allocated_amount) * 100
        return Decimal('0')