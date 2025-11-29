# apps/courses/serializers.py
from rest_framework import serializers
from apps.courses.models import Course, Enrollment, CourseInstructor


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    enrolled_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_name', 'course_type', 'subject', 'description',
            'fee_per_month', 'max_students', 'duration_months',
            'schedule_days', 'schedule_time', 'classroom',
            'start_date', 'end_date', 'status',
            'enrolled_count', 'is_full', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'enrolled_count', 'is_full']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'course', 'course_name',
            'enrollment_date', 'status', 'final_grade', 'completion_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate enrollment"""
        course = data.get('course')
        
        # Check if course is full
        if course and course.is_full:
            raise serializers.ValidationError({
                'course': 'Course is at full capacity'
            })
        
        # Check for duplicate enrollment
        student = data.get('student')
        if Enrollment.objects.filter(
            student=student,
            course=course,
            status='active'
        ).exists():
            raise serializers.ValidationError({
                'student': 'Student is already enrolled in this course'
            })
        
        return data
