#!/usr/bin/env python2
"""
An HTTP wrapper around the Polychart Query Service. This allows one to send query
requests via HTTP requests, and recieve data through HTTP responses.
"""
import json
import re
import sys

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from traceback import format_exc

import polychartQuery

def main(configFilePath, port):
  with open(configFilePath) as f:
    config = json.load(f)
  for dsKey in config['data_sources'].keys():
    if not re.match('[A-Za-z0-9_-]+$', dsKey):
      raise ValueError('data source key %s contains invalid character' % json.dumps(dsKey))

  connectionPool = {}

  class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
      self.send_response(200)
      self.end_headers()
      self.wfile.write('Polychart Query Service')

    def do_POST(self):
      if self.path == '/data-source':
        try:
          req = json.loads(self.rfile.read(int(self.headers['Content-Length'])))

          result = processDsRequest(req, config, connectionPool)

          self.send_response(200)
          self.send_header('Content-Type', 'application/json')
          self.end_headers()
          json.dump(result, self.wfile)
        except Exception:
          self.send_response(500)
          self.end_headers()
          self.wfile.write('Error while process data source request:\n')
          self.wfile.write(format_exc())
      else:
        self.send_response(400)
        self.end_headers()
        self.wfile.write('Unknown service %s' % repr(self.path))

  HTTPServer(('127.0.0.1', port), RequestHandler).serve_forever()

def processDsRequest(req, config, connectionPool):
  """
  Method dispatcher for Connection objects.
  """
  command = req['command']
  dsKey   = req['dataSourceKey']

  connection = getConnection(dsKey, config, connectionPool)

  if command == 'listTables':
    result = connection.listTables()
  elif command == 'getColumnMetadata':
    result = connection.getColumnMetadata(
      req['tableName'],
      req['columnExpr'],
      req['dataType']
    )
  elif command == 'queryTable':
    result = connection.queryTable(
      getFirstTableNameFromQuery(req['query']),
      req['query'],
      1000
    )
  else:
    raise ValueError('Unknown data source command %s' % repr(command))

  return result

def getFirstTableNameFromQuery(querySpec):
  """
  Helper to obtain the first table name in a given query specification.
  """
  for _, val in querySpec['meta'].iteritems():
    if 'tableName' in val:
      return val['tableName']

  return None

def getConnection(dsKey, config, connectionPool):
  """
  Given a data source key and configuration file, either return a previously
  cached connection, or open a new connection.
  """
  if dsKey in connectionPool:
    result = connectionPool[dsKey]

    if result.opened:
      return result
    else: # Connection has died
      del connectionPool[dsKey]

  dsConfig = config['data_sources'][dsKey]
  result = polychartQuery.openConnection(**dsConfig)

  connectionPool[dsKey] = result

  return result

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print "Usage: %s <config-file-path> <port-number>" % sys.argv[0]
    sys.exit(1)

  main(sys.argv[1], int(sys.argv[2]))
