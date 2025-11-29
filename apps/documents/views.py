# apps/documents/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, DocumentTemplate
from rest_framework import serializers


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Document management"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['document_type', 'status', 'related_model']
    search_fields = ['title', 'document_number']
    ordering = ['-created_at']


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for DocumentTemplate management"""
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['template_type', 'is_active']
    ordering = ['template_type', 'name']