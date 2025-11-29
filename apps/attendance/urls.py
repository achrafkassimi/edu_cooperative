# apps/attendance/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.attendance import views

router = DefaultRouter()
router.register(r'records', views.AttendanceViewSet, basename='attendance')
router.register(r'summaries', views.AttendanceSummaryViewSet, basename='attendance-summary')

urlpatterns = [
    path('', include(router.urls)),
]