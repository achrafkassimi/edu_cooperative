# apps/payments/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.payments import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'plans', views.PaymentPlanViewSet, basename='payment-plan')

urlpatterns = [
    path('', include(router.urls)),
]