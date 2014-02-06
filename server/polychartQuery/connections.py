"""
A Singleton-like module for managing datasource connections.

Attribs:
  _CONNECTION_POOL: A dictionary containing active datasource connections. The keys are the
    a pair with first member session key and second member data source key; the
    values are the datasource connection object.

Exported:
  runMethod: A function which dispatches datasource connection methods.
  getConnection: Find a connection with a given key.
  RedirectRequired: An exception that carries redirect information

Private Methods:
  _saveConnection: Saves a connection in the data source pool.
  _createDsArgs: Helper to change from client side data source arguments to backend ones.
"""
from logging import getLogger

from polychart.main.models   import DataSource, LocalDataSource, PendingDataSource
from polychartQuery.abstract import DsConnError
from polychartQuery.oauth    import oauthRedirect

#
# Module Constants
#

SQL_DATABASES = ['mysql', 'postgresql', 'infobright']
OAUTH_CONNECTIONS = ['googleAnalytics']
LOCAL_DATA_SOURCES = ['csv']

logger = getLogger(__name__)

#
# Public Functions
#

def createDataSource(request, clientDsObj):
  """
  Method to create a data source.

  Args:
    request: Django request object; used for secure storage key, Django user object
      and session key.
    clientDsObj: A dictionary containing arguments for creating a data source connection.
      See `_createDsArgs` for more details.

  Returns:
    A dictionary with a field 'status'.

    If the data source was successfully created, then 'status' will be
    'success' and a 'key' field will have value corresponding to the data
    source key of the new data source.

    In the case that something went wrong, 'status' will be 'error', and an
    'error' field will contain a description of what went wrong.
  """
  user             = request.user
  secureStorageKey = request.session['secureStorageKey']
  sessionKey       = request.session.session_key

  dsArgs = _createDsArgs(clientDsObj, user)
  ds     = DataSource.create(secureStorageKey, dsArgs)

  try: # Try opening connection before saving
    dsConn = ds.openConnection(request, secureStorageKey)
    ds.save()

    # See if there are any pending data sources, especially with local data
    if 'key' in clientDsObj:
      try:
        pds = PendingDataSource.objects.get(key=str(clientDsObj['key']))
        try:
          lds = LocalDataSource.objects.get(pendingdatasource=pds)
          lds.datasource = ds
          lds.pendingdatasource = None
          lds.save()
        except LocalDataSource.DoesNotExist:
          pass
        pds.delete()
      except PendingDataSource.DoesNotExist:
        pass

    # Cache connection for later
    _saveConnection(sessionKey, ds.key, dsConn)

    return {
      'status': 'success'
    , 'key': ds.key
    }
  except DsConnError as err:
    logger.exception('Connection error setting up data source connection during create')
    return {
      'status': 'error'
    , 'error': {
        'type': 'connection'
      , 'message': err.message
      }
    }
  except Exception as err:
    logger.exception('Unexpected error setting up data source connection during create')
    return {
      'status': 'error'
    , 'error': {
        'type': 'unknown'
      }
    }

def getConnection(request, dsKey):
  """
  Method to attempt to get a specifc connection from the connection pool.

  Args:
    request: Django request object; needed for the secure storage key and session
      key.
    dsKey: The datasource key corresponding to desired datasource.

  Returns:
    A data source connection object.
  """
  sessionKey = request.session.session_key

  dsConn = _CONNECTION_POOL.get((sessionKey, dsKey))

  if dsConn and dsConn.opened:
    return dsConn
  elif dsConn: # Connection has died, remove from pool
    del _CONNECTION_POOL[(sessionKey, dsKey)]

  # pylint: disable = E1101
  # For some reason, pylint does not recognize Django models as having 'objects' attribute
  dataSource = DataSource.objects.get(user=request.user, key=dsKey)
  dsConn = dataSource.openConnection(request, request.session['secureStorageKey'])

  _saveConnection(sessionKey, dsKey, dsConn)

  return dsConn

class RedirectRequired(Exception):
  """
  Exception class for actions that require redirects.

  Attribs:
    url: A string corresponding to the redirect destination.
  """
  def __init__(self, url):
    self.url = url
    super(RedirectRequired, self).__init__()

#
# Private Functions
#

_CONNECTION_POOL = {}

def _saveConnection(sessionKey, dsKey, connection):
  """
  Method to handle caching of data sources.

  Args:
    sessionKey: A Django session key.
    dsKey: The datasource key corresponding to the data source.
    connection: An object representing the data source connection.

  Returns:
    Void; simply stashes the connection in the _CONNECTION_POOL variable.
  """
  _CONNECTION_POOL[(sessionKey, dsKey)] = connection



def _createDsArgs(clientDsObj, user):
  """
  Method to transform the dictionary arguments provided by client-side code to
  a dictionary usable as keyword arguments when creating a data source.

  Args:
    clientDsObj: A dictionary holding information for creating a data source
      connection. The dictionary is of the following form:
        { name: "Data Source Name"
        , type: "MySQL"
        , connectionType: "ssh"
        , dbUsername: "root"
        , dbPassword: "mypass"
        , dbName: "database_name"
        , dbHost: "localhost"
        , dbPort: "5013"
        , ...
        }
    user: A Django user object.

  Returns:
    A dictionary that may be used in one of the data source adapters uesd.
  """
  dsType = str(clientDsObj['type'])
  dsArgs = { 'name': str(clientDsObj['name'])
           , 'type': dsType
           , 'user': user }
  if dsType in SQL_DATABASES:
    dsArgs.update(
        { 'connection_type':  str(clientDsObj['connectionType'])
        , 'db_username':      str(clientDsObj['dbUsername'])
        , 'db_password':      str(clientDsObj['dbPassword'])
        , 'db_name':          str(clientDsObj['dbName'])
        }
    )
    if dsArgs['connection_type'] == 'direct':
      dsArgs.update(
          { 'db_host': str(clientDsObj['dbHost'])
          , 'db_port': int(clientDsObj['dbPort'])
          }
      )
      if 'dbSslCert' in clientDsObj:
        dsArgs['db_ssl_cert'] = str(clientDsObj['dbSslCert'])

    elif dsArgs['connection_type'] == 'ssh':
      dsArgs.update(
          { 'ssh_username':   str(clientDsObj['sshUsername'])
          , 'ssh_host':       str(clientDsObj['sshHost'])
          , 'ssh_port':       int(clientDsObj['sshPort'])
          , 'ssh_key':        str(clientDsObj['sshKey'])
          , 'db_unix_socket': str(clientDsObj['dbUnixSocket'])
          }
      )
    else:
      raise ValueError( "dataSources.connection._createDsArgs"
                      , "Invalid connection type: {0}".format(dsArgs['connection_type']))

  elif dsType in OAUTH_CONNECTIONS:
    if 'refresh_token' in clientDsObj:
      dsArgs['oauth_refresh_token'] = str(clientDsObj['refresh_token'])
      dsArgs['ga_profile_id'] = str(clientDsObj['gaId'])
    else:
      if dsType == 'googleAnalytics':
        # pass both name AND gaId
        name = dsArgs['name'] + "||" + str(clientDsObj['gaId'])
        raise RedirectRequired(oauthRedirect('ga', name))
  elif dsType not in LOCAL_DATA_SOURCES:
    raise ValueError( "dataSources.connection._createDsArgs"
                    , "Invalid data source type: {0}".format(dsArgs['type']))
  return dsArgs
