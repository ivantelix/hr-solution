import os
from django.core.wsgi import get_wsgi_application

# Apunta a settings de producción por defecto para WSGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.prod')
application = get_wsgi_application()
