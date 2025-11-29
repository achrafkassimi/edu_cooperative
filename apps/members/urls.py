from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.members import views

router = DefaultRouter()
router.register(r'', views.MemberViewSet, basename='member')

urlpatterns = [
    path('', include(router.urls)),
]