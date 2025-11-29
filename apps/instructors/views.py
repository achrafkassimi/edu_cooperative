# apps/instructors/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Instructor
from .serializers import InstructorSerializer


class InstructorViewSet(viewsets.ModelViewSet):
    """ViewSet for Instructor management"""
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'employment_type', 'specialization']
    search_fields = ['full_name', 'email', 'specialization']
    ordering_fields = ['full_name', 'hire_date']
    ordering = ['full_name']