"""
Defines how Django should route HTTP requests to views.
Some applications have their own routing files.
See `polychart.*.urls`.
"""

import polychart.main.urls as MAIN_URLS

try:
  import polychart.site.urls as SITE_URLS
except ImportError:
  SITE_URLS = None

try:
  import polychart.jsSite.urls as JS_SITE_URLS
except ImportError:
  JS_SITE_URLS = None

try:
  import polychart.analytics.urls as ANALYTICS_URLS
except ImportError:
  ANALYTICS_URLS = None

from django.conf.urls import include, patterns, url
from polychart.utils import permanentRedirect

def _buildPatternList():
  urls = [
    # Main website
    url(r'^', include(SITE_URLS)) if SITE_URLS else None,

    # Main app
    url(r'^', include(MAIN_URLS)),

    # Polychart.js website
    url(r'^js/', include(JS_SITE_URLS)) if JS_SITE_URLS else None,

    # Analytics
    url('^', include(ANALYTICS_URLS)) if ANALYTICS_URLS else None,

    # Deprecated URLs
    url(r'^beta$', permanentRedirect('/signup')),
    url(r'^devkit.*$', permanentRedirect('/')),
    url(r'^embed/.*$', permanentRedirect('/')),
  ]

  # Filter out None
  urls = [x for x in urls if x]

  return patterns('polychart.main.views', *urls)

urlpatterns = _buildPatternList()
