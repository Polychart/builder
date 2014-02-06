"""
Module that defines the abstract interface for DataSourceConnection objects.
This module also defines the `retry` decorator and a few error classes.
"""
import traceback

from base64    import urlsafe_b64encode
from functools import wraps
from logging   import getLogger
from hashlib   import sha256
from os        import urandom
from time      import time

logger = getLogger(__name__)

class DsConnError(Exception):
  """
  Thrown to indicate that a data source connection experienced an error.
  This may require action from the end user.
  """
  def __init__(self, causeExcInfo):
    Exception.__init__(self, str(causeExcInfo))
    self.cause = causeExcInfo

class DsConnClosedError(DsConnError):
  """
  Thrown to indicate that a data source connection is no longer active,
  but recreating the connection could fix the problem.
  """
  def __str__(self):
    result = 'Data source closed due to exception:\n'
    result += ''.join(traceback.format_exception(*self.cause))
    return result

class DataSourceConnection(object):
  """
  Represents an active connection to some data source.
  Abstract class.
  See also: polychart.main.models.DataSource.openConnection
  """
  def __init__(self, *args, **kwargs):
    self._cacheId = randomCode()
    pass

  def listTables(self):
    """
    List tables is called by the client during the initial loading phase of the
    dashboard builder. The server will fetch information about what sort of tables
    are available to the user, and also the associated data columns within those
    tables.

    Returns:
      An array of tables.
    """
    raise NotImplementedError('data source connection did not implement listTables')

  def getColumnMetadata(self, tableName, columnExpr, dataType):
    """
    This method fetches meta data for a given column and table name. The main use
    of this function is to grab the range information for use of filtering in the
    front end.

    Args:
      tableName: The name of the table containing the column.
      columnExpr: The column name and expression to get the data for
      dataType: The type of the data elements.

    Returns:
      A metadata object.
    """
    raise NotImplementedError('data source connection did not implement getColumnMetadata')

  def queryTable(self, tableName, querySpec, limit):
    """
    Any querying action posed by the clientside code will pass its request to this
    method.

    Args:
      tableName: The name of the table containing the column.
      querySpec: A dictionary containing the query information. It is of the
        following form
          { select: ["columnOne", "columnTwo"]
          , meta:   {columnOne: {type: "num"}, columnTwo: {type: "cat"} }
          , stats:  { groups: ["columnTwo"]
                    , stats:  [{key: "columnOne", name: {"count(columnOne"}, stat: "count"}]
                    }
          , filters: {columnOne: {ge: 1337, le: 9000}}
          , trans:   [{key: "columnOne", trans: "bin", bw: "3.141582"}]
          }
      limit: An integer specifying the maximum number of results to return. If
        not provided, 1000 is default.
    """
    raise NotImplementedError('data source connection did not implement queryTable')

  def generateCacheKey(self, querySql, params):
    """
    Internal helper for caching.
    """
    parts = [self._cacheId, querySql, params]
    hashedParts = sha256(repr(parts)).hexdigest()
    return __name__ + '::' + hashedParts

#### Helper functions

def randomCode():
  """Generate 18 random bytes."""
  return urlsafe_b64encode(urandom(18))

def retry(retryLimit):
  """Decorator to run a function a given amount of times."""
  def wrapper(func):
    # pylint: disable = C0111
    @wraps(func)
    def wrapped_func(*args):
      runCount = 0
      while runCount < retryLimit:
        try:
          startTime = time()
          result = func(*args)
          logger.info("Function {0} took {1} seconds.".format(func.__name__, time() - startTime))
          return result
        except Exception:
          logger.exception("Lost connection to data source; retrying.")
          runCount += 1
      logger.exception("Retried {0} times; aborting.".format(retryLimit))
      return None
    return wrapped_func
  return wrapper
