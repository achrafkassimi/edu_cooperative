# apps/financials/services.py
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone

from apps.financials.models import (
    InstructorPayment, MonthlyFinancial, 
    MemberDistribution, Expense
)
from apps.instructors.models import Instructor
from apps.members.models import Member
from apps.payments.models import Payment
from apps.courses.models import CourseInstructor


class FinancialCalculationService:
    """Service for financial calculations"""
    
    @staticmethod
    def calculate_instructor_payments(period_month):
        """
        Calculate and create instructor payment records for a given period
        
        Args:
            period_month: date object for first day of the month
            
        Returns:
            List of created InstructorPayment objects
        """
        # Get first and last day of the period
        first_day = period_month.replace(day=1)
        if period_month.month == 12:
            last_day = period_month.replace(year=period_month.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = period_month.replace(month=period_month.month + 1, day=1) - timedelta(days=1)
        
        payments = []
        
        # Get all active instructors
        instructors = Instructor.objects.filter(status='active')
        
        for instructor in instructors:
            # Calculate total hours for the period
            total_hours = CourseInstructor.objects.filter(
                instructor=instructor,
                course__start_date__lte=last_day,
                course__end_date__gte=first_day
            ).aggregate(
                total=Sum('hours_taught')
            )['total'] or Decimal('0')
            
            if total_hours > 0:
                # Create or update payment record
                payment, created = InstructorPayment.objects.update_or_create(
                    instructor=instructor,
                    period_month=first_day,
                    defaults={
                        'total_hours': total_hours,
                        'hourly_rate': instructor.hourly_rate,
                        'status': 'pending'
                    }
                )
                
                # Calculate amounts
                payment.calculate_amounts()
                payments.append(payment)
        
        return payments
    
    @staticmethod
    def calculate_monthly_profit(period_month, retained_earnings_percentage=20):
        """
        Calculate monthly profit and create distribution records
        
        Args:
            period_month: date object for first day of the month
            retained_earnings_percentage: percentage to retain (default 20%)
            
        Returns:
            MonthlyFinancial object
        """
        first_day = period_month.replace(day=1)
        if period_month.month == 12:
            last_day = period_month.replace(year=period_month.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = period_month.replace(month=period_month.month + 1, day=1) - timedelta(days=1)
        
        # Calculate total revenue (paid payments)
        total_revenue = Payment.objects.filter(
            payment_date__gte=first_day,
            payment_date__lte=last_day,
            status='paid'
        ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
        
        # Calculate instructor payments
        instructor_payments_total = InstructorPayment.objects.filter(
            period_month=first_day,
            status__in=['approved', 'paid']
        ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0')
        
        # Calculate operational expenses
        operational_expenses = Expense.objects.filter(
            period_month=first_day,
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Create or update monthly financial summary
        summary, created = MonthlyFinancial.objects.update_or_create(
            period_month=first_day,
            defaults={
                'total_revenue': total_revenue,
                'instructor_payments': instructor_payments_total,
                'operational_expenses': operational_expenses,
                'other_expenses': Decimal('0')
            }
        )
        
        # Calculate totals
        summary.calculate_totals()
        
        # Calculate retained earnings and distributable profit
        retained = summary.gross_profit * (Decimal(retained_earnings_percentage) / 100)
        summary.retained_earnings = retained
        summary.distributable_profit = summary.gross_profit - retained
        summary.save()
        
        # Create member distributions if profit is positive
        if summary.distributable_profit > 0:
            FinancialCalculationService._create_member_distributions(summary)
        
        return summary
    
    @staticmethod
    def _create_member_distributions(monthly_financial):
        """Create distribution records for members"""
        # Get all active members who can receive profit
        members = Member.objects.filter(
            status='active'
        )
        
        # Calculate total share percentage
        total_shares = sum(m.share_percentage for m in members)
        
        if total_shares == 0:
            return []
        
        distributions = []
        for member in members:
            # Calculate distribution amount
            share_percentage = member.share_percentage
            amount = (monthly_financial.distributable_profit * share_percentage) / 100
            
            # Create distribution record
            distribution, created = MemberDistribution.objects.update_or_create(
                member=member,
                monthly_financial=monthly_financial,
                defaults={
                    'share_percentage': share_percentage,
                    'amount': amount,
                    'status': 'pending' if member.can_receive_profit else 'cancelled',
                    'is_public_employee': member.employment_status == 'public'
                }
            )
            distributions.append(distribution)
        
        return distributions
    
    @staticmethod
    def get_financial_summary(period_month):
        """Get financial summary for a period"""
        first_day = period_month.replace(day=1)
        
        try:
            summary = MonthlyFinancial.objects.get(period_month=first_day)
            
            return {
                'period': first_day.strftime('%B %Y'),
                'total_revenue': float(summary.total_revenue),
                'total_expenses': float(summary.total_expenses),
                'gross_profit': float(summary.gross_profit),
                'retained_earnings': float(summary.retained_earnings),
                'distributable_profit': float(summary.distributable_profit),
                'profit_margin': float(summary.profit_margin),
                'is_finalized': summary.is_finalized
            }
        except MonthlyFinancial.DoesNotExist:
            return None
    
    @staticmethod
    def get_dashboard_kpis():
        """Get dashboard KPIs"""
        from apps.students.models import Student
        from apps.courses.models import Course, Enrollment
        
        # Current month
        today = date.today()
        current_month = today.replace(day=1)
        
        # Get current month summary
        try:
            current_summary = MonthlyFinancial.objects.get(period_month=current_month)
        except MonthlyFinancial.DoesNotExist:
            current_summary = None
        
        # Calculate pending payments
        pending_payments = Payment.objects.filter(
            status='pending',
            due_date__lte=today
        ).aggregate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        return {
            'total_students': Student.objects.filter(status='active').count(),
            'total_courses': Course.objects.filter(status='active').count(),
            'total_enrollments': Enrollment.objects.filter(status='active').count(),
            'pending_payments_count': pending_payments['count'] or 0,
            'pending_payments_amount': float(pending_payments['total'] or 0),
            'current_month_revenue': float(current_summary.total_revenue) if current_summary else 0,
            'current_month_profit': float(current_summary.gross_profit) if current_summary else 0
        }