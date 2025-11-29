# apps/financials/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date

from apps.financials.models import MonthlyFinancial
from apps.financials.services import FinancialCalculationService


class FinancialViewSet(viewsets.ViewSet):
    """ViewSet for financial operations"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calculate_instructor_payments(self, request):
        """Calculate instructor payments for a period"""
        period_month = request.data.get('period_month')
        
        if not period_month:
            return Response(
                {'error': 'period_month is required (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            period = date.fromisoformat(period_month)
            payments = FinancialCalculationService.calculate_instructor_payments(period)
            
            return Response({
                'message': f'Calculated {len(payments)} instructor payments',
                'period': period_month,
                'total_payments': len(payments)
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def calculate_monthly_profit(self, request):
        """Calculate monthly profit and distributions"""
        period_month = request.data.get('period_month')
        retained_percentage = request.data.get('retained_earnings_percentage', 20)
        
        if not period_month:
            return Response(
                {'error': 'period_month is required (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            period = date.fromisoformat(period_month)
            summary = FinancialCalculationService.calculate_monthly_profit(
                period, 
                retained_percentage
            )
            
            return Response({
                'message': 'Monthly profit calculated successfully',
                'period': period_month,
                'revenue': float(summary.total_revenue),
                'gross_profit': float(summary.gross_profit),
                'distributable_profit': float(summary.distributable_profit)
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get financial summary for a period"""
        period_month = request.query_params.get('period_month')
        
        if not period_month:
            return Response(
                {'error': 'period_month query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            period = date.fromisoformat(period_month)
            summary = FinancialCalculationService.get_financial_summary(period)
            
            if not summary:
                return Response(
                    {'error': 'No financial data for this period'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(summary)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard KPIs"""
        kpis = FinancialCalculationService.get_dashboard_kpis()
        return Response(kpis)