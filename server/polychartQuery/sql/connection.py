"""
Module implementing connection to a SQL-like database.
"""
from logging import getLogger
from sys     import exc_info
from time    import time

import os

from polychartQuery.sql.query import ( SqlQuery
                                     , PostgreSqlQuery
                                     , getType
                                     , createSshUnixSocket )
from polychartQuery.abstract  import ( DataSourceConnection
                                     , DsConnError
                                     , DsConnClosedError
                                     , retry )
from polychartQuery.utils     import ( saneEncode
                                     , getNewTempFilePath
                                     , listDictWithPair )
from polychartQuery.sql.expr import exprToMySql, exprToPostgres
from polychartQuery.expr import exprCallFnc, getExprValidator

logger = getLogger(__name__)

class SqlConn(DataSourceConnection):
  """
  Class representing data source connections for SQL-like databases.

  Attribs:
    db: Object representing an active database connection.
    dbName: The database name to use.
    opened: Flag denoting whether or not the database connection is active.
    queryType: Class object denoting the query implementation to use.
    _cacheId: ID unique to this connection to be used for caching.

  Public Methods:
    listTables: Lists tables; see DataSourceConnection.listTables.
    queryTable: Queries tables; see DataSourceConnection.queryTable.
    getColumnMetadata: Metadata for columns; see DataSourceConnection.geteColumnMetadata.

  Private Methods:
    _connect: Method to help with connecting to the data base adapter.
    _getAllColumns: Helper to query for all columns in the database.
    _getColumnsInTable: Helper to query for all columns in a table.
    _getColumn: Helper to query information about a given column.
  """
  def __init__(self,  **kwargs):
    super(SqlConn, self).__init__()
    self.opened = False

    sslCert = kwargs.get('db_ssl_cert')
    if sslCert is not None:
      # Write certificate to temp file for MySQL to access
      # Yeah, this sucks.
      certFilePath = getNewTempFilePath()
      with open(certFilePath, 'w') as f:
        f.write(sslCert)

      kwargs['db_ssl_cert_path'] = certFilePath

    self.db        = self._connect(**kwargs)
    self.dbName    = kwargs['db_name']
    self.opened    = True
    self.queryType = SqlQuery

    if sslCert is not None:
      os.remove(certFilePath)

  ### DataSourceConnection method implementations

  @retry(2)
  def listTables(self):
    """
    Lists tables for general SQL data sources. See
    DataSourceConnection.listTables for more information.
    """
    cur_result = self._getAllColumns()
    result     = []

    for tableName, columnName, dataType in cur_result:
      table = listDictWithPair(result, 'name', tableName)
      if table is None:
        table = { 'name': tableName, 'meta': {} }
        result.append(table)
      polyType                  = getType(dataType)
      table['meta'][columnName] = { 'type': polyType }

      if polyType == 'date' and dataType in ['day', 'month', 'year']:
        table['meta'][columnName]['timerange'] = dataType

    return result

  @retry(2)
  def getColumnMetadata(self, tableName, columnExpr, dataType):
    """
    Returns the meta data for a given column. See DataSourceConnection.getColumnMetadata
    for more information.

    Raises:
      ValueError: Thrown when columnName is not found in table.
    """
    columns = []
    for col in self._getColumnsInTable(tableName):
      columns += ["{0}.{1}".format(tableName, col[0])]
    validate = getExprValidator(columns)
    validate(columnExpr)

    expr = columnExpr['expr']
    result = {}
    if dataType == 'cat':
      columns = self._query(
        'SELECT distinct({col}) FROM {table} LIMIT 100'.format(
          col   = self._translate(expr)
        , table = tableName)
      )

      def sanitize(v):
        if v is None:
          return "Null"
        return v
      result = { "values" : [sanitize(v[0]) for v in columns if len(v) > 0] }
    else:
      min = exprCallFnc('min', [expr])
      max = exprCallFnc('max', [expr])

      if dataType == 'date':
        q = "SELECT {colMin},{colMax} FROM {table}".format(
              colMin = self._translate(exprCallFnc('unix', [min]))
            , colMax = self._translate(exprCallFnc('unix', [max]))
            , table  = tableName)
      elif dataType == 'num':
        q = "SELECT {colMin},{colMax} FROM {table}".format(
              colMin = self._translate(min)
            , colMax = self._translate(max)
            , table  = tableName)
      columns = self._query(q)
      if len(columns) > 0:
        minValue, maxValue = columns[0]
      else:
        minValue, maxValue = (0, 0)
      result = { "min" : minValue
               , "max" : maxValue }

    return result

  @retry(2)
  def queryTable(self, tableName, querySpec, limit):
    """
    Queries the SQL database and returns the result. See
    DataSourceConnection.queryTable for more information.

    Raises:
      ValueError: Thrown when the querySpec is not a dictionary.
    """
    if not isinstance(querySpec, dict):
      raise ValueError( "sql.connSql.SqlConn.queryTable"
                      , "Invalid parameter type: {0}".format(type(querySpec)))

    # IMPORTANT: This prevents SQL injections by validating table name

    tableNames = []
    if '_additionalInfo' in querySpec['meta']:
      tableNames = querySpec['meta']['_additionalInfo']['joins']['tables']
    if len(tableNames) == 0 and tableName:
      tableNames = [tableName]

    columns = []
    for table in tableNames:
      for col in self._getColumnsInTable(table):
        columns += [("{0}.{1}".format(table, col[0]), col[1])]
    if not columns:
      raise ValueError( "sql.connSql.SqlConn.queryTable"
                      , "Unknown table name: {table}".format(table=tableName))

    for colName, colType in columns:
      name     = colName
      trans    = listDictWithPair(querySpec['trans'], 'key', colName)
      transKey = None
      if trans is not None:
        transKey = trans['key']
        name     = trans['name']
      if colName in querySpec['select'] or\
         colName in querySpec['filter'] or\
         colName == transKey:
        if name not in querySpec['meta']:
          querySpec['meta'][name] = {}
        querySpec['meta'][name]['type'] = getType(colType)

    # Perform table query using translator
    query  = self.queryType(tableName, querySpec, limit, self._query, columns)
    result = query.getData()
    return saneEncode(result)

  ### Internal Methods

  def _query(self, querySql, params=None):
    """
    Internal query function. Queries the SQL database with caching on our end.

    Args:
      querySql: A string corresponding to the SQL query to be made, possibly
        with format parameters to be filled in by the database driver.
      params: A tuple of arguments to be interpolated into the SQL query by
        the database driver. This must match the number of spots in the string.

    Returns:
      A tuple of tuples as the result of the query. Each inner tuple is ordered
      same as the order which names appeared in the query.
    """
    import MySQLdb

    try:
      startTime = time()

      cur = self.db.cursor()
      cur.execute(querySql, params)
      result = cur.fetchall()
      cur.close()

      logger.info('SQL data source query took {0}s'.format(time()-startTime))

      return result
    except Exception as err:
      try:
        cur.close()
      except Exception:
        pass

      if isinstance(err, MySQLdb.OperationalError):
        # 'MySQL server has gone away'
        if err.args[0] == 2006:
          self.close()
          raise DsConnClosedError(exc_info())

      logger.info("Problematic query: {0}".format(querySql))
      logger.info("Parameters: {0}".format(params))

      # Probably a connection error, reset just in case
      self.close()
      raise

  def _connect(self, db_username, db_password, db_name, connection_type,
      db_host = None, db_port = None, db_ssl_cert_path = None,
      db_unix_socket = None, ssh_host = None, ssh_port = None,
      ssh_username = None, ssh_key = None, **kwargs):
    # pylint: disable = R0913, R0914, W0613
    # R0913: Unfortunately, this function needs this many arguments
    # R0914: Need local vars due to arguments
    # W0613: Need **kwargs because dictionary is passed indiscriminately in
    import MySQLdb
    """
    Helper function for connecting to a database driver.
    """
    connArgs = { 'user':   db_username
               , 'passwd': db_password
               , 'db':     db_name }
    if connection_type == 'direct':
      connArgs.update({ 'host': db_host
                      , 'port': db_port })

      if db_ssl_cert_path:
        connArgs['ssl'] = { 'ca': db_ssl_cert_path }
    elif connection_type == 'ssh':
      connArgs.update({ 'host':        'localhost'
                      , 'unix_socket': createSshUnixSocket( db_unix_socket
                                                          , ssh_username
                                                          , ssh_host
                                                          , ssh_port
                                                          , ssh_key )})
    else:
      raise ValueError( "sql.connection.SqlConn._connect"
                      , "No connection method for data source" )
    try:
      db = MySQLdb.connect(**connArgs)
      db.autocommit(True)
      return db
    except MySQLdb.OperationalError as err:
      raise DsConnError('OperationalError: {msg}'.format(msg = err.args[1]))

  def close(self):
    """Helper to close database if it is open."""
    if self.opened:
      self.opened = False
      self.db.close()

  def __del__(self):
    """Internal method to ensure connection closed upon garbage collection."""
    self.close()

  ### Convenience methods for common queries

  def _getAllColumns(self):
    """Helper to get columns and data types of a database."""
    return self._query(
      '''
      SELECT table_name, column_name, data_type
      FROM information_schema.columns
      WHERE table_schema=%s
      ''',
      self.dbName
    )

  def _getColumnsInTable(self, tableName):
    """Helper to get columns and data types of a table."""
    return self._query(
      '''
      SELECT column_name, data_type
      FROM information_schema.columns
      WHERE table_schema=%s
      AND table_name=%s
      ''',
      (self.dbName, tableName)
    )

  def _getColumn(self, tableName, columnName):
    """Helper to get a specific column."""
    return self._query(
      '''
      SELECT column_name, data_type
      FROM information_schema.columns
      WHERE table_schema=%s
      AND table_name=%s
      AND column_name=%s
      ''',
      (self.dbName, tableName, columnName)
    )

  #
  # Abstract Methods
  #   To be implemented by concrete instances.
  def _translate(self, expr):
    """
    Method to combine individual pieces of a query

    Args:
      expr: A column expression

    Returns:
      A string that represents the same expression in the data source type
    """
    raise NotImplementedError()

### Specific SQL implementations

class MySqlConn(SqlConn):
  """
  Data source connection representing a MySQl data source. This is exactly the
  same as the base SQL source, so see SqlConn for more details.
  """
  def _translate(self, expr):
    return exprToMySql(expr)


class InfobrightConn(SqlConn):
  """
  Data source connection representing a Infobright data source. This is exactly
  the same as the base SQL source, so see SqlConn for more details.
  """
  pass

class PostgreSqlConn(SqlConn):
  """
  Data source connection representing a PostgreSQL data source. There are some
  differences in syntax and features in Postgres, so there are some overrides
  in terms of internal methods.
  """
  def __init__(self,  **kwargs):
    super(PostgreSqlConn, self).__init__(**kwargs)
    self.queryType = PostgreSqlQuery

  def _translate(self, expr):
    return exprToPostgres(expr)

  @retry(2)
  def queryTable(self, tableName, querySpec, limit):
    """
    Queries the SQL database and returns the result. Overrides SqlConn.queryTable
    due to differences in how PostgreSQL handles schemas.

    Raises:
      ValueError: Thrown when the querySpec is not a dictionary.
    """
    if not isinstance(querySpec, dict):
      raise ValueError( "sql.connSql.PostgreSQL.queryTable"
                      , "Invalid parameter type: {0}".format(type(querySpec)))

    # IMPORTANT: This prevents SQL injections by validating table name
    columns = [("{0}.{1}".format(tableName, col[0]), col[1])
                  for col in self._getColumnsInTable(tableName)]
    if not columns:
      raise ValueError( "sql.connSql.PostgreSQL.queryTable"
                      , "Unknown table name: {0}".format(tableName))

    schema = self._getTableSchema(tableName)
    if schema != [] and schema[0][0] != 'public':
      tableName = schema[0][0] + '.' + tableName

    if 'meta' not in querySpec or querySpec['meta'] == {}:
      meta = {colName: {'type': getType(colType)} for colName, colType in columns}
      querySpec['meta'] = meta

    query  = self.queryType(tableName, querySpec, limit, self._query, columns)
    result = query.getData()
    return saneEncode(result)


  def _connect(self, db_host, db_port, db_username, db_password, db_name, **kwargs):
    """
    Overrides _connect method in SqlConn for the simpler connection offered by
    the PostgreSQL adapter.

    Args:
      db_host: String for data base host.
      db_port: String for data base port.
      db_username: String for data base user.
      db_password: String for data base password corresponding to given user.
      db_name: String for table schema that is to be used.

    Returns:
      If the connection is successful, the active database connection is returned.

    Raises:
      DsConnError: Thrown in case of an error during connection.
    """
    connArgs = { 'host':     db_host
               , 'port':     int(db_port)
               , 'user':     db_username
               , 'password': db_password
               , 'dbname':   db_name
               }
    try:
      import psycopg2
      db            = psycopg2.connect(**connArgs)
      db.autocommit = True
      return db
    except psycopg2.OperationalError as err:
      raise DsConnError('OperationalError: ' + str(err.message))


  ### Convenience functions for common queries

  def _getAllColumns(self):
    """Helper to get all columns in a given table schema."""
    return self._query(
      '''
      SELECT table_name, column_name, data_type
      FROM information_schema.columns
      WHERE table_schema<>'information_schema'
      AND table_schema<>'pg_catalog'
      '''
    )

  def _getColumnsInTable(self, tableName):
    """Helper to get all columns in a table."""
    return self._query(
      '''
      SELECT column_name, data_type
      FROM information_schema.columns
      WHERE table_schema<>'information_schema'
      AND table_schema<>'pg_catalog'
      AND table_name=%s
      ''',
      (tableName,)
    )

  def _getColumn(self, tableName, columnName):
    """Helper to get a specific column."""
    return self._query(
      '''
      SELECT column_name, data_type
      FROM information_schema.columns
      WHERE table_name=%s
      AND column_name=%s
      ''',
      (tableName, columnName)
    )

  def _getTableSchema(self, tableName):
    """Helper to get the table schema a particlar table is in."""
    return self._query(
      '''
      SELECT distinct table_schema
      FROM information_schema.columns
      WHERE table_name=%s
      ''',
      (tableName,)
    )
