# apps/students/admin.py
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'parent_name', 'parent_phone', 'status', 'registration_date']
    list_filter = ['status', 'education_level', 'gender']
    search_fields = ['full_name', 'parent_name', 'email']
    date_hierarchy = 'registration_date'
    
# Repeat for all models