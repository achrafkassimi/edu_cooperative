# apps/courses/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.courses.models import Course, Enrollment
from apps.courses.serializers import CourseSerializer, EnrollmentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course management"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course_type', 'status', 'subject']
    search_fields = ['course_name', 'subject', 'description']
    ordering_fields = ['course_name', 'start_date', 'fee_per_month']
    ordering = ['-start_date']
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get enrolled students"""
        course = self.get_object()
        enrollments = Enrollment.objects.filter(
            course=course,
            status='active'
        ).select_related('student')
        
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def enroll_student(self, request, pk=None):
        """Enroll a student in this course"""
        course = self.get_object()
        
        # Check capacity
        if course.is_full:
            return Response(
                {'error': 'Course is at full capacity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student_id = request.data.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment
        from apps.students.models import Student
        from datetime import date
        
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check for duplicate
        if Enrollment.objects.filter(
            student=student,
            course=course,
            status='active'
        ).exists():
            return Response(
                {'error': 'Student already enrolled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment = Enrollment.objects.create(
            student=student,
            course=course,
            enrollment_date=date.today(),
            status='active'
        )
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Enrollment management"""
    queryset = Enrollment.objects.all().select_related('student', 'course')
    serializer_class = EnrollmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'course', 'status']
