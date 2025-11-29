# apps/attendance/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import date

from .models import Attendance, AttendanceSummary
from .serializers import AttendanceSerializer, AttendanceSummarySerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for Attendance management"""
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'status', 'date']
    search_fields = ['student__full_name', 'course__course_name']
    ordering_fields = ['date']
    ordering = ['-date']
    
    @action(detail=False, methods=['post'])
    def bulk_record(self, request):
        """Record attendance for multiple students"""
        records = request.data.get('records', [])
        
        if not records:
            return Response(
                {'error': 'No records provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_records = []
        errors = []
        
        for record_data in records:
            serializer = AttendanceSerializer(data=record_data)
            if serializer.is_valid():
                serializer.save()
                created_records.append(serializer.data)
            else:
                errors.append({
                    'data': record_data,
                    'errors': serializer.errors
                })
        
        return Response({
            'created': len(created_records),
            'failed': len(errors),
            'records': created_records,
            'errors': errors
        }, status=status.HTTP_201_CREATED if created_records else status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_course_date(self, request):
        """Get attendance records for a course on a specific date"""
        course_id = request.query_params.get('course_id')
        date_str = request.query_params.get('date')
        
        if not course_id or not date_str:
            return Response(
                {'error': 'course_id and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            attendance_date = date.fromisoformat(date_str)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        records = Attendance.objects.filter(
            course_id=course_id,
            date=attendance_date
        ).select_related('student', 'course')
        
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)


class AttendanceSummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for AttendanceSummary management"""
    queryset = AttendanceSummary.objects.all()
    serializer_class = AttendanceSummarySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'course', 'month']
    ordering = ['-month']
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate attendance summary"""
        summary = self.get_object()
        summary.calculate_summary()
        
        serializer = self.get_serializer(summary)
        return Response({
            'message': 'Summary recalculated successfully',
            'data': serializer.data
        })