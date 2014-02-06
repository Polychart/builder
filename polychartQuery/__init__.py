"""
Provide a public interface for constructing new SQL-esque data sources.
"""
from polychartQuery.sql import MySqlConn, InfobrightConn, PostgreSqlConn

__all__ = []

def openConnection(type, *args, **kwargs):
  if type == 'mysql':
    return MySqlConn(*args, **kwargs)

  elif type == 'infobright':
    return InfobrightConn(*args, **kwargs)

  elif type == 'postgresql':
    return PostgreSqlConn(*args, **kwargs)
