from django.urls import path
from . import web_views

urlpatterns = [
    path('', web_views.DashboardView.as_view(), name='dashboard'),
    path('login/', web_views.LoginView.as_view(), name='login'),
    path('logout/', web_views.LogoutView.as_view(), name='logout'),
    path('profile/', web_views.ProfileView.as_view(), name='profile'),
    path('settings/', web_views.SettingsView.as_view(), name='settings'),
]