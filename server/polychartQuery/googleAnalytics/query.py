"""
Implementation of Google Analytics Querying for Polychart Dashboard Builder
"""
import time
import re

from polychartQuery.query                  import DbbQuery
from polychartQuery.googleAnalytics.params import GAParams
from polychartQuery.utils                  import listDictWithPair
from polychartQuery.googleAnalytics.expr   import exprToGA

class GAQuery(DbbQuery):
  """
  A class implementing querying for Google Analytics.

  Attribs:
    startDate: String representing the startdate for queries.
    endDate: String representing the enddate for queries.
    gaId: String representing the Google Analytics Profile ID for queries.

  Private Methods:
    _checkDate: Utility to check that query dates are within bound.
    _combinePieces: Method to combine the individual pieces of a query. See
      dataSources.query.DbbQuery for more information.
    _executeQuery: Method that actually executes the query. See
      dataSources.query.DbbQuery for more information.
    _formatResult: Method that formats result from the query to a usable form.
      See dataSources.query.DbbQuery for more information.
    _formatRows: Method that takes individual rows of raw data from Google
      Analytics and returns a formatted array.
    _formatTimeData: Method that takes data involving time and formats it,
      dealing with binning and the like.
    _tryParseDate: Method that tries to return a date in Unix timestamp format.
    _validateQuery: Method that performs basic validation on a Google Analytics query.
  """
  _monthBins = { 'twomonth': 2
               , 'quarter':  4
               , 'sixmonth': 6
               }
  _yearBins  = { 'twoyear':  2
               , 'fiveyear': 5
               , 'decade':  10
               }

  def _translate(self, expr):
    return exprToGA(expr)

  def __init__(self, tableName, jsSpec,
               limit=1000, queryFunc=None, startDate=None, endDate=None, gaId=None):
    self.startDate = startDate
    self.endDate   = endDate
    self.gaId      = gaId
    DbbQuery.__init__(self, tableName, jsSpec, limit, queryFunc)

  def _combinePieces(self, queryFields, joins, groups, filters):
    """
    Combines the various query fields. See dataSources.query._combinePieces
    for more information.
    """
    args = { 'ids':         'ga:{0}'.format(self.gaId)
           , 'start-date':  self.startDate
           , 'end-date':    self.endDate }

    for i, sel in enumerate(self.select):
      meta, jsSelect = None, self.selectOrder[i]
      if jsSelect in self.jsSpec['meta']:
        meta = self.jsSpec['meta'][jsSelect]
      else:
        for table in GAParams.getTables():
          if jsSelect in table['meta']:
            meta = table['meta'][jsSelect]
            break
      if re.match(".*\.time", sel) is not None:
        sel = 'date' # If 'time' queried without binning
      sel = getColumnName(sel, meta.get('tableName', None))
      if meta['ga'] == 'metric':
        args['metrics'] = maybeAddWithComma(args.get('metrics', ''), 'ga:%s' % sel)
      elif meta['ga'] == 'dimension':
        args['dimensions'] = maybeAddWithComma(args.get('dimensions', ''), 'ga:%s' % sel)
      self.select[i] = sel

    for obj in filters:
      filt = obj['name']

      filtName = getColumnName(filt)
      if filtName == 'time':
        for op, val in obj.iteritems():
          if op not in ['in', 'ge', 'le', 'lt', 'gt', 'eq']:
            continue
          # To deal with the default values of filters
          if   val == 0:
            val = self._tryParseDate(self.startDate)
          elif val == 10:
            val = time.time()
          date = time.strftime('%Y-%m-%d', time.gmtime(val))
          if op in ('ge', 'gt'):
            args['start-date'] = date
          elif op in ('lt', 'le'):
            args['end-date']   = date
      # TODO: Optimize filtering of dimensions
      else:
        upper, lower  = None, None
        gaType, comma, fQuery = None, False, ""
        for table in GAParams.getTables():
          if filt in table['meta']:
            gaType = table['meta'][filt]['ga']
            filtName = getColumnName(filt, table['name'])
        for op, val in obj.iteritems():
          if op not in ['in', 'ge', 'le', 'lt', 'gt', 'eq']:
            continue
          if comma:
            fQuery += ','
          else:
            comma = True
          if op == 'in':
            query = ['ga:{filt}=={item}'.format(filt=filtName, item=item) for item in val]
            fQuery += ','.join(query)
          elif gaType == 'metric':
            fQuery += 'ga:' + str(filt)
            if op   == 'ge':
              fQuery += ">="
            elif op == 'le':
              fQuery += "<="
            elif op == 'eq':
              fQuery += "=="
            fQuery += str(val)
          else:
            if   op == 'le':
              upper = val
            elif op == 'ge':
              lower = val
            elif op == 'eq':
              lower = upper = val
        if lower and upper:
          query = ['ga:{filt}=={value}'.format(filt=filtName, value=i) for i in xrange(lower, upper+1)]
          fQuery += ','.join(query)
        if 'filters' in args:
          args['filters'] += fQuery
        else:
          args['filters']  = fQuery
    # TODO: Allow for AND filtering---the current filtering method is OR only.
    if 'filters' in args and args['filters'][0] == ',':
      args['filters'] = args['filters'][1:]

    if len(self.sort) > 0:
      fields = ['ga:{field}'.format(field=getColumnName(field)) for field in self.sort]

      vals = self.sort.values()
      for i, field in enumerate(self.sort.keys()):
        fields[i] = '-' + fields[i] if not self.sort[field].get('asc') else fields[i]
      args['sort'] = ','.join(fields)

    if self.limit:
      args['max-results'] = self.limit

    return args

  def _executeQuery(self, query):
    """
    Method that actually dispatches the query to the Google Analytics endpoint.
    See dataSources.query._executeQuery for more information.

    Args:
      query: A dictionary corresponding to a Google Analytics query object.

    Returns:
      A dicitonary response from Google Analytics.

    Raises:
      Exception: Raises an error when something wrong happens.
    """
    try:
      result = self.queryFunc(query)
      return result
    except Exception as e:
      raise e

  def _formatResult(self, result):
    """
    Implementation of _formatResult from DbbQuery.

    Args:
      result: Object representing the Google Analytics query response, in the form
        {...
        , columnHeaders: [{name: String, columnType: String, dataType: String}]
        , rows: [Strings]
        , totalsForAllResults: {name: String}
        }

    Returns:
      A dictionary containing data and meta fields. See dataSources.query._formatResult
      for more details.
    """
    try:
      rows = result['rows']
    except KeyError: # Empty result
      return {'data': [], 'meta': self.jsSpec['meta']}

    gaNames = [col['name'][3:] for col in result['columnHeaders']]
    headerNames = []
    data = None

    realNameDict = dict(zip(self.select, self.selectOrder))
    for i, name in enumerate(gaNames):
      if name in realNameDict:
        headerNames.append(realNameDict[name])
      else:
        headerNames.append(name)

    if any(re.match(r'.*\.time', s) for s in self.selectOrder):
      data = self._formatTimeData(gaNames, headerNames, realNameDict, rows)
    if data is None:
      data = [item for row in rows for item in self._formatRows(
          headerNames
        , realNameDict
        , [row])]

    for name, val in self.jsSpec['meta'].iteritems():
      if 'sort' in val:
        self.jsSpec['meta']['sorted'] = True

    return {'data': data, 'meta': self.jsSpec['meta']}

  def _validateQuery(self, query):
    """
    Basic validation of Google Analytics Query. Checks whether or not there is at
    least one metric and whether or not dates are within admissible bounds.

    Args:
      query: A Google Analytics query in the form
        { start-date: 2005-01-01
        , end-date: 2013-07-02
        , metrics: "ga:visitors,ga:..."
        , dimensions: "ga:date,ga:month"
        , filters: "ga:date==..."
        }
    Raises:
      ValueError: Thrown when something is wrong with the query.
    """
    startDate = self._tryParseDate(query['start-date'])
    endDate   = self._tryParseDate(query['end-date'])
    if 'metrics' not in query:
      raise ValueError( "googleAnalytics.query._validateQuery"
                      , "Google Analytics Queries require at least one metric!")
    elif not (self._checkDate(startDate) and self._checkDate(endDate)):
      raise ValueError( "googleAnalytics.query._validateQuery"
                      , "Dates are out of bounds: {0} {1}".format(startDate, endDate))

  def _formatTimeData(self, gaNames, headerNames, headerNamesDict, rows):
    """
    Method that formats time data. This will perform any necessary binning,
    conversion of datestrings to unix time stamps, and groupings if applicable.

    Args:
      gaNames: A list of names used by GA

      headerNamesDict: Dictionary where the keys are GA names and values
        are polyJS names. (which may not be the same)

      rows: A list of lists which correspond to the rows of data. Each row is
        ordered corresponding to the strings in the header names. All data is
        string, so any numerical data must be converted before operations are
        done on them

    Returns:
      A list of dictionaries is expected from this function. Each list entry will
      be a dictionary with keys corresponding to the field names expected by the
      dashboard builder, and the values will be the corresponding data entry for
      that row.
    """

    timeItem = None

    for column in headerNames:
      if re.match(r'.*\.time', column):
        timeItem = column # does this always exist?
        bw = self.jsSpec['meta'][column].get('bw')
        break
    if timeItem is None:
      return None

    # Check whether or not 'time' queried with or without binning
    if bw: bw = bw.lower()

    if not bw or bw == 'day':
      result = []
      idx = headerNames.index(timeItem)
      for row in rows:
        row[idx] = stringToUnixTime(row[idx], '%Y%m%d')
        result += self._formatRows(headerNames, headerNamesDict, [row])
      return result

    end          = len(rows) - 1
    tmpBin, data = [], []

    def _dataRow(bins, dateString, dateFormat='%Y%m%d', excluded=None):
      """
      Helper function to deal with the pattern of formatting rows, setting the
      date position to desired format, and appending to the data array.

      Args:
        bins: A list of data that is collected for a particular binning setting.

        dateString: A string that is in the format specified by dateFormat.

        dateFormat: An string specifying the format of the date. Conventions used
          follow those found in the `datetime` module. If no dateFormat is
          specified, then a format akin to year-month-date is expected.

        excluded: An optional list of array indicies that are not to be included
          into the result. Mainly applicable to binning.

      Returns:
        The function returns the formatted data as an array.
      """
      if bins != []:
        result = self._formatRows( headerNames
                                 , headerNamesDict
                                 , bins
                                 , excluded = excluded
                                 , groups   = self.groups )
        for res in result:
          res[timeItem] = stringToUnixTime(dateString, dateFormat)
        return result

    if bw == 'month':
      monthIdx, yearIdx = gaNames.index('month'), gaNames.index('year')
      for row in rows:
        data += _dataRow( [row]
                        , str(row[yearIdx]) + str(row[monthIdx])
                        , dateFormat = '%Y%m'
                        , excluded   = [yearIdx, monthIdx]
                        )
    elif bw == 'year':
      yearIdx = gaNames.index('year')
      for row in rows:
        data += _dataRow( [row]
                        , str(row[yearIdx])
                        , dateFormat = '%Y'
                        , excluded   = [yearIdx]
                        )

    # Formats with actual binning
    elif bw == 'week':
      dateIdx, weekIdx = gaNames.index('date'), gaNames.index('week')
      weekNumber = rows[0][weekIdx]
      for i, row in enumerate(rows):
        if row[weekIdx] == weekNumber:
          tmpBin.append(row)
        elif tmpBin != [] or (i == end and tmpBin != []):
          data += _dataRow( tmpBin
                          , tmpBin[0][dateIdx]
                          , excluded = [weekIdx, dateIdx]
                          )
          tmpBin, weekNumber = [row], row[weekIdx]
    elif bw in self._monthBins:
      monthIdx, yearIdx = gaNames.index('month'), gaNames.index('year')
      for i, row in enumerate(rows):
        tmpBin.append(row)
        if int(row[monthIdx]) % int(self._monthBins[bw]) == 0 or i == end:
          data += _dataRow( tmpBin
                          , str(tmpBin[0][yearIdx])+str(tmpBin[0][monthIdx])
                          , dateFormat = '%Y%m'
                          , excluded   = [monthIdx, yearIdx]
                          )
          tmpBin = []
    elif bw in self._yearBins:
      yearIdx =  gaNames.index('year')
      for i, row in enumerate(rows):
        tmpBin.append(row)
        if int(row[yearIdx]) % int(self._yearBins[bw]) == 0 or i == end:
          data += _dataRow( tmpBin
                          , str(tmpBin[0][yearIdx])
                          , dateFormat = '%Y'
                          , excluded   = [yearIdx]
                          )
          tmpBin = []

    return data

  def _checkDate(self, date):
    """
    Checks that the provided date is between the startdate and today.

    Args:
      date: A date to be checked.
    Returns:
      A boolean representing whether or not the provided date is between admissible
      bounds.
    """
    parsedDate = self._tryParseDate(date)
    return self._tryParseDate(self.startDate) <= parsedDate <= time.time()

  @staticmethod
  def _tryParseDate(date):
    """
    Tries to parse date with time utility. If it fails, assume that proper
    format already.

    Args:
      date: Date string with format YYYY-MM-DD

    Returns:
      Unix timestamp for date.
    """
    try:
      return time.mktime(time.strptime(date, '%Y-%m-%d'))
    except Exception:
      return date

  def _formatRows(self, headerNames, headerNamesDict, bins, excluded=None, groups=None):
    """
    Formats a row of data provided by Google Analytics.

    Args:
      headerNames: A list of strings that denote the header names for each list
        position.
      bins: A list of data that is to be processed, ordered in the same order as
        the header names.
      excluded: An optional list of indicies that are not to be aggregated.
        Mainly used for binning.
      groups: An optional list of header names that denote additional groupings
        beside numerical or date bins.

    Returns:
      The result shall be an array of dictionaries, with keys corresponding to
      header names and values corresponding to the aggregated data.
    """
    result = []
    groupings, groupIdx = [], 0
    if excluded is None:
      excluded = []
    if False and groups is not None: #TODO: Fix this!
      for group in groups:
        if not re.match(r'bin\(.*\.time,.+\)', group):
          for spec in self.spec:
            if spec['name'] == group:
              group = spec['fieldName']
              break
          groupIdx = headerNames.index(group)
          excluded.append(groupIdx)
          for binRow in bins:
            if binRow[groupIdx] not in groupings:
              groupings.append(binRow[groupIdx])
              result.append({group: binRow[groupIdx]})
          # Assumed that there is only one grouping beside time bins
          break
    if groupings == []:
      result.append({})

    for binRow in bins:
      rowGroupIdx = 0
      if groupIdx:
        rowGroupIdx = groupings.index(binRow[groupIdx])
      for i, datum in enumerate(binRow):
        if i not in excluded:
          name = headerNames[i]
          try:
            if name in result[rowGroupIdx]:
              result[rowGroupIdx][name] += float(datum)
            else:
              result[rowGroupIdx][name]  = float(datum)
          except ValueError:
            result[rowGroupIdx][name] = datum
    return result

#### Helper functions
def stringToUnixTime(string, form):
  """Given string of date and the format, returns time stamp."""
  return int(time.mktime(time.strptime(string, form)))

def getColumnName(name, tableName=None):
  """
  Attempts to extract the column name given a string. Looks for a string in the
  form "{tableName}.{columName}".

  Args:
    name: The string to process.
    tableName: Optional; if given, this is looked for in the string.

  Returns:
    A string that is hopefully processed.
  """
  try:
    if tableName:
      pattern = re.compile(r'.*(?:%s\.)(.*)' % tableName)
      match = pattern.match(name)
      if match is None:
        return name
      else:
        return match.group(1)
    else:
      if name.find('.') != -1:
        return name[name.find('.')+1:]
      else:
        return name
  except (ValueError, TypeError):
    return name

def maybeAddWithComma(baseString, newString):
  """
  Appends a new string to a base string, adding a comma in between if the base
  is non empty.

  Args:
    baseString: Original string on which to append on.
    newString: New string to be appended.

  Returns:
    A string in the form `baseString` appended with `newString`, with a comma
    preceeding `newString` if `baseString` is nonempty, otherwise, just `newString`.
  """
  if baseString == "":
    return newString
  else:
    return baseString + ',' + newString
