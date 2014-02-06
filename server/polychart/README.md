Polychart Dashboard Builder Backend
===================================
Herein lies the backend code for the Polychart Dashboard Builder. The server is
written in Python and is built atop of the [Django] (https://www.djangoproject.com/)
web framework. The primary directories here are `config/` and `main/`; the
former contains Django-related configuration files that provide settings to the
Django environment, with the possibility of differing setups in a local
development environment and a production environment; the latter directory
contains the actual logic and code for Dashboard Builder related processing. For
a detailed description of the contents of each directory, see the documents
contained in the individual directories.

Within this directory lie three main files.

First, `urls.py` determines the collection of URL patterns to be given to the
application. This file is written in such a way that it may collect the URL
patterns for a variety of applications, add to it some other predetermined
patterns, and package them up for the Django application as a whole.

The other two files, `utils.py` and `wsgi.py` are rather short and
self-explanatory: the first defines a collection of Django-related utility
functions that are oft used in View Handler functions and the latter defines the
[WSGI] (http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) application
settings for the Django environment.
