Django Configuration
====================
Here we will outline the basics of the Django configuration files, and sketch
how they are used in the Polychart Dashboard Builder application. See the
[documentation](https://docs.djangoproject.com/en/dev/topics/settings/) for
more details on what Django settings are to look like, and how to write more
detailed settings files.

Within the Dashboard Builder backend code, there are three settings modules
that are used: `local`, `deploy`, and `shared`.  `local` defines settings that
apply when the server is run in a local development environment.  `deploy`
defines settings that apply when the server is deployed on a server.  `shared`
defines settings that apply to both environments.

Setting Overrides
-----------------
Often times, however, one will need to provide settings that contain sensitive
information: database credentials, API secret keys, and magic strings, for
example. These settings probably do not wish to appear in version control, and
thus should not be placed in one of the settings files mentioned above. Instead,
Polychart's Dashboard Builder backend provides the option to override settings
defined in any of `local.py`, `deploy.py` or `shared.py` by the files
`localOverrides.py`, `deployOverrides.py and `overrides.py`, which each append
to the settings of `local.py`, `deploy.py` and `shared.py`, but with the
settings contained in these override modules taking precedence.

With these override files, one can then provide generic settings in the usual
configuration files, and then add some private settings conditionally. For
example, one can configure `local.py` to look for a SQLite database by default,
and use that as a store of data in a development environment, but one can,
locally, force Django to use a MySQL server instead.

Polychart Dashboard Builder Settings
------------------------------------
Along with most of the usual Django settings, the Dashboard Builder has a
variety of internal settings that allow one to toggle certain features, and to
provide credentials for others. The following is a list of some notable
settings:

  * `ENABLED_DATA_SOURCE_TYPES`: This list determines which data sources will be
    available in the Dashboard Builder. The values of the list may take on the
    following: `'mysql'`, `'infobright'`, `'postgresql'`, `'csv'`, and
    `'googleAnalytics`'
  * `GOOGLE_ANALYTICS_CLIENT_ID`: A Google Analytics API OAuth 2.0 client ID
    obtained from their [API console] [0]. This setting is required if the
    Google Analytics data source is enabled.
  * `GOOGLE_ANALYTICS_CLIENT_SECRET`: A Google Analytics API OAuth 2.0 client
    secret obtained from their [API console] [0]. This setting is requierd if
    the Google Analytics data source is enabled.
  * `INTERCOM_ENABLED`, `OLARK_ENABLED`, `SEGMENT_IO_ENABLED`,
    `USERVOICE_ENABLED`: Flags that toggle certain third party extensions.
  * `SIGNUP_ENABLED`: Flag to toggle whether or not a signup feature is to be
    shown in the Dashboard Builder interface.

[0]: https://code.google.com/apis/console/
