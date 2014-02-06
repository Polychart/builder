"""
Project settings for production-like deployments.

Settings in this file are overridden by values in
polychart.config.deployOverrides.
"""

from polychart.config.shared import *

DEBUG = False
TEMPLATE_DEBUG = False

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

try:
  from polychart.config.deployOverrides import *
except ImportError:
  pass
