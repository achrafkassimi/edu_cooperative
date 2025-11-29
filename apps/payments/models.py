# apps/payments/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import date, timedelta
from apps.students.models import Student
from apps.courses.models import Enrollment


class Payment(models.Model):
    """Student payment model"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('mobile_payment', 'Mobile Payment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='payments',
        db_index = True
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='payments',
        blank=True,
        null=True,
        db_index = True
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True
    )
    
    # Dates
    due_date = models.DateField(db_index = True)
    payment_date = models.DateField(blank=True, null=True, db_index = True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index = True)
    
    # References
    receipt_number = models.CharField(max_length=50, unique=True, blank=True, null=True, db_index = True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # db_index = True
        # indexes = [
        #     models.Index(fields=['student', 'status']),
        #     models.Index(fields=['enrollment', 'status']),
        #     models.Index(fields=['due_date']),
        #     models.Index(fields=['payment_date']),
        #     models.Index(fields=['status']),
        #     models.Index(fields=['receipt_number']),
        # ]
        ordering = ['-due_date', '-created_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.amount} DH - {self.status}"
    
    @property
    def balance(self):
        """Remaining balance"""
        return self.amount - self.amount_paid
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        return self.status in ['pending', 'partially_paid'] and self.due_date < date.today()
    
    @property
    def days_overdue(self):
        """Number of days overdue"""
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0
    
    def mark_as_paid(self, amount=None, payment_method=None):
        """Mark payment as paid"""
        if amount is None:
            amount = self.amount
        
        self.amount_paid = amount
        self.payment_date = date.today()
        
        if payment_method:
            self.payment_method = payment_method
        
        if self.amount_paid >= self.amount:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partially_paid'
        
        self.save()


class Invoice(models.Model):
    """Invoice model for payment tracking"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='invoices',
        db_index = True
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='invoices',
        blank=True,
        null=True
    )
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True, db_index = True)
    invoice_date = models.DateField(default=date.today, db_index = True)
    due_date = models.DateField(db_index = True)
    
    # Amounts
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index = True)
    
    # Payment tracking
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='invoice'
    )
    
    # Document
    pdf_path = models.CharField(max_length=500, blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # db_index = True
        # indexes = [
        #     models.Index(fields=['student', 'status']),
        #     models.Index(fields=['invoice_number']),
        #     models.Index(fields=['invoice_date']),
        #     models.Index(fields=['due_date']),
        #     models.Index(fields=['status']),
        # ]
        ordering = ['-invoice_date', '-invoice_number']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.student.full_name}"
    
    def save(self, *args, **kwargs):
        # Calculate total if not set
        if not self.total:
            self.total = self.subtotal - self.discount + self.tax
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.status in ['sent', 'draft'] and self.due_date < date.today()


class PaymentPlan(models.Model):
    """Installment payment plan for students"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='payment_plans'
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='payment_plans'
    )
    
    # Plan details
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    installment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    number_of_installments = models.PositiveIntegerField()
    
    # Dates
    start_date = models.DateField(default=date.today)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['enrollment', 'status']),
        ]
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.number_of_installments} installments"
    
    @property
    def amount_paid(self):
        """Total amount paid so far"""
        return self.installments.filter(
            status='paid'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    
    @property
    def balance(self):
        """Remaining balance"""
        return self.total_amount - self.amount_paid
    
    def generate_installments(self):
        """Generate installment payment records"""
        from apps.payments.models import Payment
        
        for i in range(self.number_of_installments):
            due_date = self.start_date + timedelta(days=30 * i)
            Payment.objects.create(
                student=self.student,
                enrollment=self.enrollment,
                amount=self.installment_amount,
                due_date=due_date,
                status='pending',
                notes=f"Installment {i+1} of {self.number_of_installments}"
            )