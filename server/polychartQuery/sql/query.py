"""
Implementation of SQL querying for Polychart Dashboard Builder
"""
from time import sleep
from subprocess import Popen

import atexit
import os

from polychartQuery.query import DbbQuery
from polychartQuery.sql.expr import exprToMySql, exprToPostgres
from polychartQuery.utils import getNewTempFilePath, listDictWithPair

import polychartQuery.validate as validate # filepath, linuxUsername, hostname
from polychartQuery.expr import exprCallFnc

class SqlQuery(DbbQuery):
  def _translate(self, expr):
    return exprToMySql(expr)

  def _combinePieces(self, queryFields, joins, groups, filters):
    select = ",".join(queryFields)
    query = 'SELECT {col} FROM {table} '.format(col = select, table = self.tableName)
    params = []

    # Join all tables and apply predicates later. This algorithm only works
    # for inner joins - more work will need to be done here in order to support
    # left/right/outer joins.
    joinedTables = [self.tableName]
    for (table1, table2), _ in joins:
      if table1 not in joinedTables:
        query += "INNER JOIN {0} ".format(table1)
        joinedTables.append(table1)
      if table2 not in joinedTables:
        query += "INNER JOIN {0} ".format(table2)
        joinedTables.append(table2)

    isFirst = True
    for _, predicates in joins:
      for pred in predicates:
        if isFirst:
          query += "ON {0} ".format(pred)
          isFirst = False
        else:
          query += "AND {0} ".format(pred)

    idx = 0
    for obj in filters:
      # To keep unix time stamp consistent
      metaKey = obj['name']
      if not metaKey in self.jsSpec['meta']:
        raise ValueError( "dataSources.sql.query._combinePieces"
                        , "No meta info for {field}.".format(field=metaKey))
      if self.jsSpec['meta'][metaKey]['type'] == 'date':
        # redo the translation?
        expr = obj['expr']['expr']
        obj['translated'] = self._translate(exprCallFnc('unix', [expr]))

      field = obj['translated']
      querytmp = ''
      if 'in' in obj:
        val = obj['in']
        querytmp += field + ' IN (' + ','.join('%s' for i in val) + ') '
        params += val
      for op in ['ge', 'le', 'lt', 'gt', 'eq']:
        if op in obj:
          val = obj[op]
          _infixop = {
            'ge' : '>=',
            'gt' : '>',
            'le' : '<=',
            'lt' : '<',
            'eq' : '=='
          }
          if querytmp != '':
            querytmp += ' AND '
          querytmp += field + _infixop[op] + ' %s '
          params.append(val)
      if 'notnull' in obj:
        if obj['notnull']:
          if querytmp != '':
            querytmp = '( ' + querytmp + ' ) AND ' + field + ' IS NOT NULL'
          else:
            querytmp = field + ' IS NOT NULL'
        else:
          if querytmp != '':
            querytmp = '( ' + querytmp + ' ) OR ' + field + ' IS NULL'

      if idx == 0:
        query += 'WHERE %s ' % querytmp
      else:
        query += 'AND %s ' % querytmp
      idx += 1

    if len(groups) > 0:
      query += 'GROUP BY {groups} '.format(groups = ','.join(groups))

    if len(self.sort) > 0:
      fields = []
      for key, asc in self.sort.iteritems():
        if asc:
          dir = " ASC "
        else:
          dir = " DESC "
        fields.append(key + dir)
      query += 'ORDER BY {orders} '.format(orders = ','.join(fields))
    if self.limit: query += 'LIMIT {lim}'.format(lim = str(self.limit))

    return (query, params)

  def _executeQuery(self, args):
    query, params = args
    result = self.queryFunc(query, params)
    return result

  def _formatResult(self, result):
    results = []
    for row in result:
      tmp = {}
      for i, name in enumerate(self.selectOrder):
        rowType = self.jsSpec['meta'][name]['type']
        if (rowType == 'date' or rowType == 'num') and row[i] is None:
          tmp[name] = 0
        else:
          tmp[name] = str(row[i])
      results.append(tmp)

    return {'data': results, 'meta': self.jsSpec['meta'] }


class PostgreSqlQuery(SqlQuery):
  def _translate(self, expr):
    return exprToPostgres(expr)

### Misc Helpers for SQL Datasources
def getType(t):
  return SQL_TYPE_MAP.get(t) or \
         PSQL_TYPE_MAP.get(t) or \
         PSQL_TYPE_MAP.get(t.split(' ')[0]) or \
         'cat'

# Blocking: do not run on main thread
def createSshUnixSocket(remoteUnixSocketPath, username, host, port, sshKey):
  if not validate.filepath(remoteUnixSocketPath):
    raise ValueError( "sql.query.createSshUnixSocket"
                    , "File path not permitted: '{path}'".format(path=remoteUnixSocketPath))
  if not validate.linuxUsername(username):
    raise ValueError( "sql.query.createSshUnixSocket"
                    , "Invalid ssh username: '{user}'".format(user=username))
  if not validate.hostname(host):
    raise ValueError( "sql.query.createSshUnixSocket"
                    , "Invalid ssh hostname: '{host}'".format(host=host))

  port                = int(port)
  localUnixSocketPath = getNewTempFilePath()
  sshKeyPath          = getNewTempFilePath()

  # 0600 permissions required by ssh
  with os.fdopen(os.open(sshKeyPath, os.O_WRONLY | os.O_CREAT, 0600), 'w') as f:
    f.write(sshKey)

  cmd = [
    'socat',
    'UNIX-LISTEN:{socketPath},reuseaddr,fork'.format(socketPath = localUnixSocketPath),
    'EXEC:"ssh -2 -o \"StrictHostKeyChecking=no\" -o \"PasswordAuthentication=no\" ' \
     + '-p {port} -i {keyPath} {user}@{host} socat STDIO UNIX-CONNECT\:{remote}"'.format(
         port    = port
       , keyPath = sshKeyPath
       , user    = username
       , host    = host
       , remote  = remoteUnixSocketPath
       )
  ]
  proc = Popen(cmd)

  # Kill child process on exit
  def onExit():
    proc.kill()
  atexit.register(onExit)

  # Wait 300 ms for socat to get set up
  # Racy...
  sleep(0.3)

  return localUnixSocketPath

### SQL and PostGreSQL type maps
# see http://kimbriggs.com/computers/computer-notes/mysql-notes/mysql-data-types-50.file
SQL_TYPE_MAP = { 'tinyint': 'num'
               , 'smallint': 'num'
               , 'mediumint': 'num'
               , 'int': 'num'
               , 'bigint': 'num'
               , 'float': 'num'
               , 'double': 'num'
               , 'decimal': 'num'
               , 'date': 'date'
               , 'datetime': 'date'
               , 'time': 'date'
               , 'timestamp': 'date'
               , 'year': 'date'
               , 'bit': 'cat'
               , 'char': 'cat'
               , 'tinytext': 'cat'
               , 'text': 'cat'
               , 'mediumtext': 'cat'
               , 'longtext': 'cat'
               , 'binary': 'cat'
               , 'tinyblob': 'cat'
               , 'blob': 'cat'
               , 'mediumblob': 'cat'
               , 'longblob': 'cat'
               , 'enum': 'cat'
               , 'set': 'cat'
               , 'varchar': 'cat'
               }

# Additional types introduced by PostgreSQL
PSQL_TYPE_MAP = { 'bigserial': 'num'
                , 'double precision': 'num'
                , 'int2': 'num'
                , 'int4': 'num'
                , 'integer': 'num'
                , 'float4': 'num'
                , 'float8': 'num'
                , 'money': 'num'
                , 'numeric': 'num'
                , 'real': 'num'
                , 'serial': 'num'
                , 'serial2': 'num'
                , 'serial4': 'num'
                , 'smallserial': 'num'
                , 'bit varying': 'cat'
                , 'boolean': 'cat'
                , 'box': 'cat'
                , 'bytea': 'cat'
                , 'character varying': 'cat'
                , 'character': 'cat'
                , 'cidr': 'cat'
                , 'circle': 'cat'
                , 'inet': 'cat'
                , 'interval': 'cat' # May have to rethink this one
                , 'line': 'cat'
                , 'macaddr': 'cat'
                , 'path': 'cat'
                , 'polygon': 'cat'
                , 'text': 'cat'
                , 'tsquery': 'cat'
                , 'tsvector': 'cat'
                , 'txid_snapshot': 'cat'
                , 'uuid': 'cat'
                , 'xml': 'cat'
                , 'json': 'cat'
                , 'timestamp': 'date'
                }
