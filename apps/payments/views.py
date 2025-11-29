# apps/payments/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, Invoice, PaymentPlan
from .serializers import PaymentSerializer, InvoiceSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'status', 'payment_method']
    search_fields = ['student__full_name', 'receipt_number']
    ordering = ['-due_date']


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'status']
    search_fields = ['invoice_number', 'student__full_name']
    ordering = ['-invoice_date']


class PaymentPlanViewSet(viewsets.ModelViewSet):
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentSerializer  # Create PaymentPlanSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'status']