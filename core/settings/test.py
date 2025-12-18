from .base import *

DEBUG = False

# Usa una DB en memoria o una DB de test separada
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
