# apps/instructors/serializers.py
from rest_framework import serializers
from .models import Instructor


class InstructorSerializer(serializers.ModelSerializer):
    active_courses_count = serializers.ReadOnlyField()
    total_hours_taught = serializers.ReadOnlyField()
    total_earnings = serializers.ReadOnlyField()
    
    class Meta:
        model = Instructor
        fields = [
            'id', 'full_name', 'email', 'phone', 'address',
            'specialization', 'qualifications', 'years_of_experience',
            'employment_type', 'hire_date', 'status',
            'hourly_rate', 'tax_rate_percentage',
            'bank_name', 'account_number', 'rib',
            'bio', 'notes',
            'active_courses_count', 'total_hours_taught', 'total_earnings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']