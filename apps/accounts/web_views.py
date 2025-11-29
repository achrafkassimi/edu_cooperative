# apps/accounts/web_views.py (Web Views)
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import LoginForm


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view"""
    template_name = 'dashboard/index.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Import models
        from apps.students.models import Student
        from apps.courses.models import Course, Enrollment
        from apps.payments.models import Payment
        from apps.financials.models import MonthlyFinancial
        from datetime import date
        from decimal import Decimal
        
        # Get statistics
        context['total_students'] = Student.objects.filter(status='active').count()
        context['total_courses'] = Course.objects.filter(status='active').count()
        context['total_enrollments'] = Enrollment.objects.filter(status='active').count()
        
        # Payment statistics
        pending_payments = Payment.objects.filter(status='pending')
        context['pending_payments_count'] = pending_payments.count()
        context['pending_payments_amount'] = sum(p.balance for p in pending_payments)
        
        # Recent students
        context['recent_students'] = Student.objects.order_by('-created_at')[:5]
        
        # Recent enrollments
        context['recent_enrollments'] = Enrollment.objects.select_related(
            'student', 'course'
        ).order_by('-created_at')[:5]
        # print(context)
        
        return context


class LoginView(View):
    """Login view"""
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Welcome back!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """Logout view"""
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'accounts/profile.html'
    login_url = 'login'


class SettingsView(LoginRequiredMixin, TemplateView):
    """User settings view"""
    template_name = 'accounts/settings.html'
    login_url = 'login'

