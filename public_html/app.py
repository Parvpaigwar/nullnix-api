import sys, os

# Django settings ka path set karo
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nullnix.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
