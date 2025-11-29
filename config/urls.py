# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API Endpoints
    path('api/students/', include('apps.students.urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/instructors/', include('apps.instructors.urls')),
    path('api/members/', include('apps.members.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/financials/', include('apps.financials.urls')),
    path('api/documents/', include('apps.documents.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    
    # Authentication
    path('api/auth/', include('apps.accounts.urls')),
    
    # Web Views
    path('', include('apps.accounts.web_urls')),  # Dashboard, login, etc.
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)