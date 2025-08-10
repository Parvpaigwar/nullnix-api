import os
import sys

# Add current dir to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nullnix.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
