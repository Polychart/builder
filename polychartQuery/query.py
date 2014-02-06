"""
Module defining the form of a data source query.
"""
from logging import getLogger
from polychartQuery.utils import isNumber, unbracket
from polychartQuery.expr import getExprValidator

logger = getLogger(__name__)

class DbbQuery(object):
  """
  An abstract class for all data source queries.

  Attribs:
    jsSpec: A dictionary corresponding to the Polychart2.js data query object,
            of the form
      { select:
         [ { name: "columnOne", expr: columnOneExpr }
         , { name: "columnTwo", expr: columnTwoExpr }
         , ...]
      , meta:   {columnOne: {type: "num"}, columnTwo: {type: "cat"}, ...}
      , stats:
          { groups: [columnOneExpr, ...]
          , stats:
              [ {args: [columnOneExpr], name: {"count(columnOne"}, name: "count"}
              , ... ]
          }
      , filters:
        [ { expr: { name: "columnOne", expr: columnOneExpr }
          , ge:   1
          , le:   2 }
        , ...]
      , sort:
        [ { key: { name: "mainColumn", expr: mainColumnExpr }
          , sort: { name: "columnToSortBy", expr: mainColumnExpr }
          , asc : True
        , ...]
      , trans:   [columnOneExpr]
      , limit: 10 // optional
      }
        WHERE columnOneExpr and columnTwoExpr are expression trees in JSON format
    tableName: A string corresponding to the table being queried.


    spec: A list of dictionaries for internal reference, in the following form
      [{name: "count(columnName)", fieldName: "columnName", functions: [binDay, unique]}, ...]
    filters: A dictionary where keys correspond to fields to be filtered, and
      values be the values; like the 'filters' field of jsSpec.
    groups: A list of strings corresponding to the columns that are to be grouped.
    sort: A dictionary with keys being column names to be sorted and value of parameters.
    limit: An integer corresponding on the limit of a result. Default is 1000.
    queryFunc: A function to be called to execute the actual query.
    query: A query object for a particular data source.

  Public Methods:
    getData: Method to be called to get data for a data source.

  Private Methods:
    _buildQuery: Method that orchestrates the pipeline of building a query for
      any data source.
    _combinePieces: Abstract method that shall take all the internal parameters
      present and combine them into a query for a particular data source.
      This is to be implemented in all concrete instances.
    _executeQuery: Abstract method that shall actually perform the query.
      This is to be implemented in all concrete instances.
    _formatResult: Abstract method that shall process a raw query response and
      produce a format usable by the Dashboard Builder.
      This is to be implemented in all concrete instances.
  """

  def __init__(self, tableName, jsSpec, limit=1000, queryFunc=None, columns=None):
    self.jsSpec = jsSpec
    self.tableName = tableName

    for filts in jsSpec['filter']: # check this
      if 'dateOptions' in filts:
        filts.pop('dateOptions')

    self.stats   = jsSpec['stats']['stats']
    self.limit   = limit
    if '_additionalInfo' in jsSpec['meta']:
      self.joins = jsSpec['meta']['_additionalInfo']['joins']['joins']
    else:
      self.joins = []
    if 'limit' in jsSpec:
      try:
        self.limit = min(self.limit, int(jsSpec['limit']))
      except:
        pass
    self.queryFunc = queryFunc

    self._validate(columns)

    self.query = self._buildQuery()

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

  #
  # Abstract Methods
  #   To be implemented by concrete instances.
  def _combinePieces(self, queryFields, joins, groups, filters):
    """
    Method to combine individual pieces of a query

    Args:
      queryFields: List of strings corresponding to the actual field names in
        the data source.
      groups: List of strings corresponding to groupings.
      filters: Dictionary of column names and parameters for filtesrs.

    Returns:
      A query object of some sort for a particular data source.
    """
    raise NotImplementedError()

  def _executeQuery(self, query):
    """
    Execute actual query and return result.

    Args:
      query: A query object suited for a particular data source

    Returns:
      The raw response from the data source.
    """
    raise NotImplementedError()

  def _formatResult(self, result):
    """
    Format the data from queries into Poly.js spec.

    Args:
      result: A raw result object straight from the data source.

    Returns:
      A dictionary with fields 'data' and 'meta'. The 'data' field shall be
      either a dictionary with keys corresponding to column headers and values
      of arrays for data rows, or an array of dictionaries, where each dictionary
      shall have keys corresponding to column headers and values corresponding
      to data point.

      The 'meta' field will be a dictionary whose fields are the column names
      and whose values are another dictionary, containing fields such as 'type',
      'range', 'bw', and others as necessary.
    """
    return result

  #
  # Concrete Methods
  #
  def getData(self):
    """
    Public method to get formatted data.
    """
    rawResult = self._executeQuery(self.query)
    result = self._formatResult(rawResult)
    return result

  def _validate(self, columns=None):
    """
    Verify that the pending query is valid. This is mainly to protect against SQL
    injection attacks. It is assumed that the table name has already been validated,
    and that some values will be parameterized.

    Args:
      columns: A list of (column_name, data_type) tuples representing the columns
      in this table.

    Returns:
      None

    Exceptions:
      ValueError
    """

    if not columns:
      logger.warn("Warning: column list not provided to query._validate!")
      logger.warn("Input validation will not occur!")
      return

    columns = [x for (x, _) in columns]
    validate = getExprValidator(columns)
    # SELECT
    for obj in self.jsSpec['select']:
      validate(obj)
    # GROUPS
    for obj in self.jsSpec['stats']['groups']:
      validate(obj)
    # FILTERS
    for obj in self.jsSpec['filter']:
      validate(obj['expr'])
    # SORTING
    for obj in self.jsSpec.get('sort', []):
      validate(obj['sort'])

  def _buildQuery(self):
    """
    From the raw queryObject, build the query piece for actual query execution

    Returns:
      A query object corresponding to the form required by a particular data source.
    """
    self.select = []
    self.selectOrder = []
    for obj in self.jsSpec['select']:
      name = obj['name']
      expr = obj['expr']
      self.selectOrder.append(unbracket(name, expr))
      self.select.append(self._translate(expr))

    self.groups = []
    for obj in self.jsSpec['stats']['groups']:
      expr = obj['expr']
      self.groups.append(self._translate(expr))

    # wow, this is so not the right way to do it...
    self.sort = {}
    for obj in self.jsSpec.get('sort', []):
      sort = self._translate(obj['sort']['expr'])
      asc = obj['asc']
      self.sort[sort] = asc

    procJoins = {}
    for joinObj in self.joins:
      pred      = "{table1}.{column1} = {table2}.{column2}".format(**joinObj)
      table1 = joinObj['table1']
      table2 = joinObj['table2']
      taple = (table1, table2) if table1 < table2 else (table2, table1)
      if taple in procJoins:
        procJoins[taple].append(pred)
      else:
        procJoins[taple] = [pred]

    self.filters = []
    for obj in self.jsSpec['filter']:
      name = obj['expr']['name']
      expr = obj['expr']['expr']
      obj['translated'] = self._translate(expr)
      obj['name'] = unbracket(name, expr)
    self.filters = self.jsSpec['filter']

    query = self._combinePieces(self.select, procJoins.items(), self.groups, self.filters)
    return query

def guessType(fieldName, vals=None):
  """
  Function to heuristically guess types, especially with unix timestamps
  """
  dateNames = ['date', 'updated', 'created', 'last_login', '_at']
  if vals and all(map(lambda x: type(x) == int, vals.values())):
    if any(map(lambda x: fieldName.lower().find(x) != -1, dateNames)): return 'date'
    else: return 'num'
  elif any(map(lambda x: fieldName.find(x) != -1, dateNames)): return 'date'
  else: return None
