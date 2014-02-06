#!/usr/bin/env python

"""
Convenient wrapper around django-admin.py.

Example usage: ./manage.py syncdb
"""

import errno
import os
import sys
from traceback import print_exc

def _mkdir(path):
  try:
    os.makedirs(path)
  except OSError as err:
    # If already exists as directory
    if err.errno == errno.EEXIST and os.path.isdir(path):
      return

    raise

if __name__ == "__main__":
  # Create directory required by logger
  _mkdir('log/app')

  # Set up environment properly
  sys.path = ['server'] + sys.path

  # Detect deployment vs local
  if os.path.isfile('server/polychart/config/deployParams.py'):
    os.environ["DJANGO_SETTINGS_MODULE"] = "polychart.config.deploy"
  else:
    os.environ["DJANGO_SETTINGS_MODULE"] = "polychart.config.local"

  # Attempt to import Django
  try:
    from django.core.management import execute_from_command_line
  except ImportError:
    print_exc()
    print
    print 'Try rerunning this command like this:'
    print '  virtualenv/bin/python2 manage.py'
    sys.exit(1)

  # Pass command-line args to Django
  execute_from_command_line(sys.argv)
