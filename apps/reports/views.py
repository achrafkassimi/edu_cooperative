# apps/reports/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Report, ReportTemplate, ReportSchedule
from rest_framework import serializers


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet for Report management"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['report_type', 'status', 'format']
    search_fields = ['title', 'description']
    ordering = ['-created_at']


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for ReportTemplate management"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_type', 'is_active']
    ordering = ['report_type', 'name']


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for ReportSchedule management"""
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'frequency']
    ordering = ['next_run_date']