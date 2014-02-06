Polychart Dashboard Builder Main Application
============================================
This directory contains the Django application for the Polychart Dashboard
Builder. The layout is typical of a Django application:

  * `models.py` define the models that are used in the database;
  * `urls.py` define the specific endpoints for which the Dashboard builder
    uses, and the corresponding handler function for these endpoints.
  * `management/` contains extensions to how `manage.py` works at the root level
    of the Django application;
  * `migrations/` contains generated and handwritten data base migrations for
    the Django application;
  * `templates/` directory contains the Django template files;
  * `utils/` directory contains an assortment of utility modules that are used
    throughout the code base;
  * `views/` directory contains handler functions that are used by the URL
    routing;

One important thing to note here is that the backend code also relies on the
Polychart Query package.
