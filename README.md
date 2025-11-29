# Django Implementation Guide - Educational Cooperative IS

## Complete 24-Week Implementation Roadmap

---

## Phase 1: Project Setup (Week 1-2)
admin@test.com
123456

### Week 1: Environment & Database Setup

#### Day 1-2: Initial Setup
```bash
# 1. Create project directory
mkdir edu_cooperative
cd edu_cooperative

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Django and dependencies
pip install -r requirements.txt

# 4. Create Django project
django-admin startproject config .

# 5. Create apps
python manage.py startapp accounts
python manage.py startapp members
python manage.py startapp students
python manage.py startapp instructors
python manage.py startapp courses
python manage.py startapp attendance
python manage.py startapp payments
python manage.py startapp financials
python manage.py startapp documents
python manage.py startapp reports
python manage.py startapp notifications
mkdir core

# 6. Move apps to apps directory
mkdir apps
mv accounts members students instructors courses attendance payments financials documents reports notifications apps/
```

#### Day 3-4: Database Configuration
```bash
# 1. Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql postgresql-contrib
# Windows: Download from postgresql.org

# 2. Create database
psql postgres
CREATE DATABASE edu_cooperative;
CREATE USER edu_user WITH PASSWORD 'your_password';
ALTER ROLE edu_user SET client_encoding TO 'utf8';
ALTER ROLE edu_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE edu_user SET timezone TO 'Africa/Casablanca';
GRANT ALL PRIVILEGES ON DATABASE edu_cooperative TO edu_user;
\q

# 3. Create .env file
cat > .env << EOF
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=edu_cooperative
DB_USER=edu_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
EOF
```

#### Day 5: Settings Configuration
```bash
# 1. Create settings structure
mkdir -p config/settings
touch config/settings/__init__.py
touch config/settings/base.py
touch config/settings/development.py
touch config/settings/production.py

# 2. Copy base settings content (from artifacts)
# 3. Update config/__init__.py to use development settings by default
```

### Week 2: Models & Migrations

#### Day 1-3: Create All Models
```bash
# 1. Implement all models (use code from artifacts)
# - apps/members/models.py
# - apps/students/models.py
# - apps/instructors/models.py
# - apps/courses/models.py
# - apps/attendance/models.py
# - apps/payments/models.py
# - apps/financials/models.py

# 2. Create migrations
python manage.py makemigrations

# 3. Review migrations
python manage.py sqlmigrate members 0001

# 4. Run migrations
python manage.py migrate
```

#### Day 4-5: Admin Configuration
```python
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
```

```bash
# Create superuser
python manage.py createsuperuser

# Run server and test admin
python manage.py runserver
# Visit: http://localhost:8000/admin
```

---

## Phase 2: Core Features (Week 3-6)

### Week 3: REST API Setup

#### Day 1-2: DRF Configuration
```bash
# 1. Install and configure DRF
pip install djangorestframework djangorestframework-simplejwt drf-spectacular

# 2. Update settings.py with REST_FRAMEWORK configuration

# 3. Create URL structure
# - config/urls.py
# - apps/*/urls.py
```

#### Day 3-5: Serializers & ViewSets
```bash
# 1. Create serializers for all models
# - apps/students/serializers.py
# - apps/courses/serializers.py
# etc.

# 2. Create ViewSets
# - apps/students/views.py
# - apps/courses/views.py
# etc.

# 3. Register URLs
# Update each app's urls.py

# 4. Test APIs
python manage.py runserver
# Visit: http://localhost:8000/api/docs/
```

### Week 4: Student & Course Management

#### Day 1-2: Student Management
```bash
# 1. Complete StudentViewSet with all actions
# 2. Add filters and search
# 3. Test CRUD operations

# Test with curl or Postman:
curl -X POST http://localhost:8000/api/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ahmed Test",
    "parent_name": "Parent Test",
    "parent_phone": "+212661234567",
    "registration_date": "2025-11-01",
    "status": "active"
  }'
```

#### Day 3-5: Course & Enrollment Management
```bash
# 1. Implement CourseViewSet
# 2. Implement EnrollmentViewSet
# 3. Add enrollment validation
# 4. Implement conflict detection
# 5. Test enrollment flow
```

### Week 5: Attendance System

#### Day 1-3: Attendance Tracking
```python
# apps/attendance/views.py
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_record(self, request):
        """Record attendance for multiple students"""
        # Implementation here
        pass

# Test bulk attendance recording
```

#### Day 4-5: Attendance Reports
```bash
# 1. Create attendance report views
# 2. Implement attendance statistics
# 3. Add date range filtering
# 4. Test report generation
```

### Week 6: Payment Processing

#### Day 1-3: Payment Management
```bash
# 1. Implement PaymentViewSet
# 2. Add payment status tracking
# 3. Implement pending/overdue logic
# 4. Test payment recording
```

#### Day 4-5: Invoice Generation
```bash
# 1. Implement InvoiceViewSet
# 2. Create invoice number generation logic
# 3. Add invoice status management
# 4. Test invoice creation
```

---

## Phase 3: Financial Automation (Week 7-10)

### Week 7: Financial Calculation Service

#### Day 1-3: Instructor Payment Calculation
```bash
# 1. Implement FinancialCalculationService
# 2. Add calculate_instructor_payments method
# 3. Test with sample data
# 4. Verify calculations match requirements

python manage.py shell
>>> from apps.financials.services import FinancialCalculationService
>>> from datetime import date
>>> period = date(2025, 11, 1)
>>> payments = FinancialCalculationService.calculate_instructor_payments(period)
>>> print(f"Created {len(payments)} payments")
```

#### Day 4-5: Profit Calculation & Distribution
```bash
# 1. Implement calculate_monthly_profit method
# 2. Add member distribution logic
# 3. Handle public employee restrictions
# 4. Test with different scenarios
```

### Week 8: Management Commands

#### Day 1-2: Financial Commands
```bash
# 1. Create calculate_monthly_financials command
# 2. Test command execution

python manage.py calculate_monthly_financials --period 2025-11-01

# 3. Verify results in database
python manage.py shell
>>> from apps.financials.models import MonthlyFinancial
>>> summary = MonthlyFinancial.objects.latest('period_month')
>>> print(f"Profit: {summary.gross_profit} DH")
```

#### Day 3-5: Data Import/Export Commands
```bash
# 1. Create import_students command
# 2. Create export commands
# 3. Test with sample CSV files

# Example CSV structure:
# full_name,parent_name,parent_phone,registration_date,status
# Ahmed Test,Parent Test,+212661234567,2025-11-01,active

python manage.py import_students students.csv
```

### Week 9-10: Celery Integration

#### Day 1-2: Celery Setup
```bash
# 1. Install Redis
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server
# Start: redis-server

# 2. Configure Celery
# Create config/celery.py

# 3. Test Celery
celery -A config worker --loglevel=info
```

#### Day 3-5: Automated Tasks
```bash
# 1. Implement all Celery tasks
# 2. Configure Celery Beat for scheduling
# 3. Test automated calculations

# Start Celery Beat
celery -A config beat --loglevel=info

# Start worker
celery -A config worker --loglevel=info
```

---

## Phase 4: Frontend & UI (Week 11-16)

### Week 11-12: API Testing & Documentation

#### Complete API Testing
```bash
# 1. Write pytest tests
# apps/students/tests.py
# apps/courses/tests.py

# 2. Run tests
pytest apps/students/tests.py -v
pytest --cov=apps

# 3. Generate API documentation
python manage.py spectacular --file schema.yml
```

### Week 13-14: Dashboard Development

#### Option A: Django Templates
```bash
# 1. Create templates/dashboard.html
# 2. Add dashboard views
# 3. Implement charts with Chart.js
# 4. Add KPI displays
```

#### Option B: React Frontend (Recommended)
```bash
# 1. Create React app
npx create-react-app frontend
cd frontend
npm install axios recharts lucide-react

# 2. Configure API endpoints
# 3. Build dashboard components
# 4. Connect to Django API

# 5. Set up CORS in Django
# Already configured in settings
```

### Week 15-16: Management Interfaces

```bash
# 1. Build student management UI
# 2. Create course scheduling interface
# 3. Implement enrollment forms
# 4. Add attendance recording UI
# 5. Create payment tracking interface
```

---

## Phase 5: Document Generation (Week 17-18)

### Week 17: PDF Generation Setup

#### Day 1-2: WeasyPrint Setup
```bash
# 1. Install WeasyPrint dependencies
# macOS: brew install cairo pango gdk-pixbuf libffi
# Ubuntu: sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

pip install weasyprint django-weasyprint
```

#### Day 3-5: Document Templates
```python
# apps/documents/generators/invoice_generator.py
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
import os

def generate_invoice_pdf(invoice_id):
    from apps.payments.models import Invoice
    
    invoice = Invoice.objects.get(id=invoice_id)
    
    # Render HTML
    html_string = render_to_string('documents/invoice_template.html', {
        'invoice': invoice,
        'student': invoice.student,
        'course': invoice.enrollment.course if invoice.enrollment else None
    })
    
    # Generate PDF
    pdf_file = HTML(string=html_string).write_pdf()
    
    # Save to media
    filename = f'invoice_{invoice.invoice_number}.pdf'
    filepath = os.path.join(settings.MEDIA_ROOT, 'invoices', filename)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(pdf_file)
    
    invoice.pdf_path = f'invoices/{filename}'
    invoice.save()
    
    return filepath
```

### Week 18: Document Views & Testing

```python
# apps/documents/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
from .generators.invoice_generator import generate_invoice_pdf

class GenerateInvoicePDF(APIView):
    def get(self, request, invoice_id):
        filepath = generate_invoice_pdf(invoice_id)
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
```

---

## Phase 6: Testing & Deployment (Week 19-24)

### Week 19-20: Comprehensive Testing

#### Unit Tests
```python
# apps/financials/tests.py
import pytest
from datetime import date
from decimal import Decimal
from apps.financials.services import FinancialCalculationService

@pytest.mark.django_db
class TestFinancialCalculations:
    def test_instructor_payment_calculation(self):
        # Setup test data
        # ...
        
        period = date(2025, 11, 1)
        payments = FinancialCalculationService.calculate_instructor_payments(period)
        
        assert len(payments) > 0
        assert payments[0].gross_amount > 0
    
    def test_profit_calculation(self):
        # Setup test data
        # ...
        
        period = date(2025, 11, 1)
        summary = FinancialCalculationService.calculate_monthly_profit(period)
        
        assert summary.gross_profit >= 0
        assert summary.distributable_profit >= 0
```

#### Integration Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Week 21: Performance Optimization

```python
# Database optimization
# 1. Add database indexes (already in models)
# 2. Use select_related and prefetch_related

# Example optimized query:
students = Student.objects.select_related('enrollments__course').prefetch_related('payments')

# 3. Add database query monitoring
pip install django-debug-toolbar

# 4. Optimize slow queries
# Use Django Debug Toolbar to identify N+1 queries
```

### Week 22: Security Hardening

```python
# config/settings/production.py
# 1. Security settings already configured

# 2. Add rate limiting
pip install django-ratelimit

# 3. Add API throttling in DRF
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# 4. Enable HTTPS and secure cookies
# Already configured in production settings
```

### Week 23: Deployment Setup

#### Server Preparation
```bash
# 1. Choose hosting (AWS, DigitalOcean, etc.)

# 2. Install dependencies on server
sudo apt-get update
sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx

# 3. Set up PostgreSQL
sudo -u postgres psql
CREATE DATABASE edu_cooperative_prod;
CREATE USER prod_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE edu_cooperative_prod TO prod_user;

# 4. Clone repository
git clone your-repo-url
cd edu_cooperative

# 5. Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure environment variables
nano .env
# Add production values

# 7. Run migrations
python manage.py migrate

# 8. Collect static files
python manage.py collectstatic

# 9. Set up Gunicorn
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# 10. Configure Nginx
sudo nano /etc/nginx/sites-available/educooperative

# 11. Set up SSL with Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Week 24: Go-Live & Training

#### Day 1-2: Final Testing
```bash
# 1. Test all features in production environment
# 2. Verify data migrations
# 3. Test backup and restore procedures

# Backup database
pg_dump edu_cooperative_prod > backup.sql

# Restore if needed
psql edu_cooperative_prod < backup.sql
```

#### Day 3-4: User Training
```bash
# 1. Create user documentation
# 2. Record video tutorials
# 3. Conduct training sessions
# 4. Provide quick reference guides
```

#### Day 5: Launch
```bash
# 1. Final smoke tests
# 2. Monitor logs
tail -f /var/log/nginx/error.log
tail -f /path/to/django/logs/django.log

# 3. Set up monitoring
pip install sentry-sdk
# Configure in settings.py

# 4. Go live!
# 5. Monitor system for first 48 hours
```

---

## Quick Command Reference

### Daily Development Commands
```bash
# Start development server
python manage.py runserver

# Make migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Celery
celery -A config worker -l info
celery -A config beat -l info

# Run tests
pytest
pytest --cov

# Shell
python manage.py shell

# Load test data
python manage.py setup_test_data

# Calculate financials
python manage.py calculate_monthly_financials --period 2025-11-01

# Send payment reminders
python manage.py send_payment_reminders --days-before 3
```

### Production Commands
```bash
# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl restart celery

# View logs
tail -f logs/django.log
journalctl -u gunicorn -f
```

---

## Success Checklist

### Phase 1: Foundation ✓
- [ ] Django project created
- [ ] PostgreSQL database configured
- [ ] All models created and migrated
- [ ] Admin interface configured

### Phase 2: Core Features ✓
- [ ] Student management working
- [ ] Course management working
- [ ] Enrollment system functional
- [ ] Attendance tracking operational
- [ ] Payment processing complete

### Phase 3: Financial Automation ✓
- [ ] Instructor payment calculation working
- [ ] Profit calculation accurate
- [ ] Member distributions correct
- [ ] Celery tasks automated
- [ ] Management commands functional

### Phase 4: UI & Documents ✓
- [ ] Dashboard displaying KPIs
- [ ] Management interfaces complete
- [ ] PDF generation working
- [ ] Reports generated correctly

### Phase 5: Testing & Deployment ✓
- [ ] All tests passing
- [ ] Performance optimized
- [ ] Security hardened
- [ ] Production deployment successful
- [ ] User training completed

---

## Support & Maintenance

### Regular Maintenance Tasks
- Weekly database backups
- Monthly security updates
- Quarterly performance reviews
- Annual feature additions

### Monitoring
- Set up error tracking (Sentry)
- Monitor server resources
- Track API usage
- Review financial calculations monthly

---

## Congratulations! 🎉

You now have a complete, production-ready Educational Cooperative Information System built with Django!