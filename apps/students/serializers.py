# apps/students/serializers.py
from rest_framework import serializers
from apps.students.models import Student


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'full_name', 'date_of_birth', 'gender', 'email', 'phone',
            'parent_name', 'parent_phone', 'parent_email', 'address',
            'education_level', 'registration_date', 'status', 'notes',
            'age', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'age']


class StudentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing students"""
    
    class Meta:
        model = Student
        fields = ['id', 'full_name', 'parent_phone', 'status', 'registration_date']
