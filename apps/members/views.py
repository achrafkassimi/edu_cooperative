# apps/members/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Member
from .serializers import MemberSerializer


class MemberViewSet(viewsets.ModelViewSet):
    """ViewSet for Member management"""
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'employment_status']
    search_fields = ['full_name', 'email', 'membership_number']
    ordering_fields = ['full_name', 'join_date']
    ordering = ['full_name']