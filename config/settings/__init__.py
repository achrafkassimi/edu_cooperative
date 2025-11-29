# config/settings/__init__.py
"""
Settings package for Educational Cooperative IS project.
Automatically loads the appropriate settings module based on DJANGO_SETTINGS_MODULE.
Defaults to development settings.
"""

import os

# Default to development settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Import the appropriate settings module
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if settings_module == 'config.settings.production':
    from .production import *
elif settings_module == 'config.settings.development':
    from .development import *
else:
    from .development import *  # Fallback to development