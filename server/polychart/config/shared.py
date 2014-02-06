"""
Django settings that are shared between local development and deployments.

Settings in this file are overridden by the values in
polychart.config.overrides, and then
polychart.config.{local,deploy}.
"""

from datetime import datetime
import os

ADMINS = (
# ('Your Name', 'name@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Toronto'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Used by login_required decorator for redirects
LOGIN_URL = '/login'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(os.path.abspath(os.getcwd()), 'allStatic')

# Additional locations of static files
STATICFILES_DIRS = (
  os.path.join(os.path.abspath(os.getcwd()), 'compiledStatic'),
  # Put strings here, like "/home/html/static" or "C:/www/django/static".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#  'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SESSION_SAVE_EVERY_REQUEST = True # used for event tracking

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
#   'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.debug',
  'django.core.context_processors.i18n',
  'django.core.context_processors.media',
  'django.core.context_processors.static',
  'django.core.context_processors.tz',
  'django.contrib.messages.context_processors.messages',
  'polychart.utils.templateContextProcessor',
)

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  # Uncomment the next line for simple clickjacking protection:
  # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'polychart.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'polychart.wsgi.application'

TEMPLATE_DIRS = (
  # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
)

def _getPolychartApps():
  result = ['polychart.main']

  try:
    import polychart.analytics
    result.append('polychart.analytics')
  except ImportError:
    pass

  try:
    import polychart.jsSite
    result.append('polychart.jsSite')
  except ImportError:
    pass

  try:
    import polychart.site
    result.append('polychart.site')
  except ImportError:
    pass

  return result

INSTALLED_APPS = _getPolychartApps() + [
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  # Uncomment the next line to enable the admin:
  # 'django.contrib.admin',
  # Uncomment the next line to enable admin documentation:
  # 'django.contrib.admindocs',

  'south',
]

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'filters': {
    'require_debug_false': {
      '()': 'django.utils.log.RequireDebugFalse',
    },
  },
  'handlers': {
    'mail_admins': {
      'level': 'ERROR',
      'filters': ['require_debug_false'],
      'class': 'django.utils.log.AdminEmailHandler',
    },
    'all_file': {
      'level': 'DEBUG',
      'class': 'logging.FileHandler',
      'filename': 'log/app/all_' + _timestamp,
    },
    'error_file': {
      'level': 'ERROR',
      'class': 'logging.FileHandler',
      'filename': 'log/app/error_' + _timestamp,
    },
    'console': {
      'level': 'DEBUG',
      'class': 'logging.StreamHandler',
    },
  },
  'loggers': {
    'django': {
      'handlers': ['mail_admins', 'all_file', 'error_file'],
      'level': 'DEBUG',
      'propagate': True,
    },
    'polychart': {
      'handlers': ['mail_admins', 'console', 'all_file', 'error_file'],
      'level': 'DEBUG',
      'propagate': True,
    },
    'polychartQuery': {
      'handlers': ['mail_admins', 'console', 'all_file', 'error_file'],
      'level': 'DEBUG',
      'propagate': True,
    },
  }
}

ENABLED_DATA_SOURCE_TYPES = [
  'mysql',
  'infobright',
  'postgresql',
  'csv',

  # Google Analytics requires additional settings:
  # GOOGLE_ANALYTICS_CLIENT_ID and GOOGLE_ANALYTICS_CLIENT_SECRET
# 'googleAnalytics',
]

INTERCOM_ENABLED = False
OLARK_ENABLED = False
SEGMENT_IO_ENABLED = False
USERVOICE_ENABLED = False

SIGNUP_ENABLED = False
ONPREM_ADS_ENABLED = False

# These features require a properly configured Django email backend
NEW_USER_EMAIL_ENABLED = False
PASSWORD_RESET_ENABLED = False

# To enable exporting, the export service must be run
# To run the exporting service: `coffee exportService/server.coffee <PORT>`
EXPORT_SERVICE_PORT = None

try:
  from polychart.config.overrides import *
except ImportError:
  pass
