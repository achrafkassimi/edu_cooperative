from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.instructors import views

router = DefaultRouter()
router.register(r'', views.InstructorViewSet, basename='instructor')

urlpatterns = [
    path('', include(router.urls)),
]