from .base import *

DEBUG = False
ALLOWED_HOSTS = ["api.tu-dominio-saas.com"]  # Reemplazar con tu dominio

# Configuración de seguridad de Producción
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
