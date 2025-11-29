# apps/payments/serializers.py
from rest_framework import serializers
from .models import Payment, Invoice, PaymentPlan


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    balance = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'student', 'student_name', 'enrollment',
            'amount', 'amount_paid', 'payment_method',
            'due_date', 'payment_date', 'status',
            'receipt_number', 'transaction_reference',
            'balance', 'is_overdue', 'days_overdue',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'student', 'student_name', 'enrollment',
            'invoice_number', 'invoice_date', 'due_date',
            'subtotal', 'discount', 'tax', 'total',
            'status', 'payment', 'pdf_path',
            'is_overdue', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total', 'created_at', 'updated_at']

