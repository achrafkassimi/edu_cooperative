# apps/documents/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'templates', views.DocumentTemplateViewSet, basename='document-template')

urlpatterns = [
    path('', include(router.urls)),
]