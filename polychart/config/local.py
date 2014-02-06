"""
Project settings used during local development.

Settings in this file are overridden by values in
polychart.config.localOverrides.
"""

from polychart.config.shared import *

DEBUG = True
TEMPLATE_DEBUG = True

# Generate your own for production deployments!
SECRET_KEY = 'TkLhoWRKORnKShe3PtdJo8jvTcm6RloPzj1sagGHbIbK3vd16U9OvZ96qvpA6TRW'

HOST_URL = 'http://localhost:8000'

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    'NAME': 'dev.db',                      # Or path to database file if using sqlite3.
    # The following settings are not used with sqlite3:
    'USER': '',
    'PASSWORD': '',
    'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
    'PORT': '',                      # Set to empty string for default.
  }
}

CACHES = {
  'default': {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'unique-snowflake',
  }
}

EMAIL_BACKEND = 'polychart.main.utils.emailConsole.ConsoleEmailBackend'

try:
  from polychart.config.localOverrides import *
except ImportError:
  pass
