import sys, os

# Project base directory add karo Python path me
sys.path.insert(0, os.path.dirname(__file__))

# Django settings ka module set karo (case match karo)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nullnix.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
