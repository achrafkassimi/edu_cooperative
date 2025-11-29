# apps/attendance/serializers.py
from rest_framework import serializers
from .models import Attendance, AttendanceSummary


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'course', 'course_name',
            'enrollment', 'date', 'status',
            'check_in_time', 'check_out_time',
            'notes', 'recorded_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceSummarySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    
    class Meta:
        model = AttendanceSummary
        fields = [
            'id', 'student', 'student_name', 'course', 'course_name',
            'month', 'total_sessions', 'present_count', 'absent_count',
            'late_count', 'excused_count', 'attendance_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
