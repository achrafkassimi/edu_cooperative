# apps/students/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from apps.students.models import Student
from apps.students.serializers import StudentSerializer, StudentListSerializer
from apps.courses.models import Enrollment
from apps.payments.models import Payment


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student CRUD operations
    
    list: Get all students
    create: Register new student
    retrieve: Get student details
    update: Update student information
    destroy: Delete student
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'education_level', 'gender']
    search_fields = ['full_name', 'parent_name', 'email', 'parent_email']
    ordering_fields = ['full_name', 'registration_date']
    ordering = ['-registration_date']
    
    def get_serializer_class(self):
        """Use lighter serializer for list action"""
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer
    
    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """Get student's enrollments"""
        student = self.get_object()
        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related('course')
        
        from apps.courses.serializers import EnrollmentSerializer
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get student's payment history"""
        student = self.get_object()
        payments = Payment.objects.filter(student=student)
        
        from apps.payments.serializers import PaymentSerializer
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get student's attendance records"""
        student = self.get_object()
        
        from apps.attendance.models import Attendance
        attendance = Attendance.objects.filter(
            student=student
        ).select_related('course')
        
        from apps.attendance.serializers import AttendanceSerializer
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get student statistics"""
        stats = {
            'total': Student.objects.count(),
            'active': Student.objects.filter(status='active').count(),
            'by_education_level': Student.objects.values('education_level').annotate(
                count=Count('id')
            ),
            'by_gender': Student.objects.values('gender').annotate(
                count=Count('id')
            )
        }
        return Response(stats)
