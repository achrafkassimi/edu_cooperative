
# apps/members/serializers.py
from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    can_receive_profit = serializers.ReadOnlyField()
    total_distributions_received = serializers.ReadOnlyField()
    
    class Meta:
        model = Member
        fields = [
            'id', 'full_name', 'email', 'phone', 'address',
            'membership_number', 'join_date', 'status',
            'employment_status', 'employer_name',
            'share_percentage',
            'bank_name', 'account_number',
            'notes',
            'can_receive_profit', 'total_distributions_received',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']