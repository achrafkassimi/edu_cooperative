# apps/members/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Member(models.Model):
    """Cooperative member model"""
    EMPLOYMENT_STATUS_CHOICES = [
        ('public', 'Public Employee'),
        ('private', 'Private Employee'),
        ('self_employed', 'Self Employed'),
        ('unemployed', 'Unemployed'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    # Membership details
    membership_number = models.CharField(max_length=50, unique=True, db_index = True)
    join_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index = True)
    
    # Employment information
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, db_index = True)
    employer_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Profit sharing
    share_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text="Member's percentage of distributable profit"
    )
    
    # Banking details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # db_index = True
        # indexes = [
        #     models.Index(fields=['membership_number']),
        #     models.Index(fields=['status']),
        #     models.Index(fields=['employment_status']),
        # ]
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} ({self.membership_number})"
    
    @property
    def can_receive_profit(self):
        """Public employees cannot receive profit distribution"""
        return self.employment_status != 'public' and self.status == 'active'
    
    @property
    def total_distributions_received(self):
        """Calculate total profit distributions received"""
        from apps.financials.models import MemberDistribution
        return MemberDistribution.objects.filter(
            member=self,
            status='paid'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')