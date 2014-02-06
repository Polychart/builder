"""
Implementation of querying for Google Analytics.
"""
from time   import time, mktime, strptime
from urllib import urlencode

import datetime
import re

from polychartQuery.abstract               import DataSourceConnection, retry
from polychartQuery.googleAnalytics.params import GAParams
from polychartQuery.googleAnalytics.query  import GAQuery
from polychartQuery.oauth                  import oauthRequest, refreshSession
from polychartQuery.utils                  import listDictWithPair, unbracket, getColumnName


RETRY_THRESHOLD = 12

class GAConn(DataSourceConnection):
  """
  A class representing a connection to the Google Analytics Reporting API.

  Attribs:
    refreshToken: An OAuth2.0 refresh token provided by Google Analytics
    accessToken: An OAuth2.0 access token granted by Google Analytics. This is
      temporary.
    gaSession: An object containing Google Analytics 'session' information; this
      includes things such as the access token and session expiry information.
    gaId: Google Analytics Profile ID. This corresponds to the ID field required
      for a Google Analytics data query.
    startDate: Beginning date for Google Analytics queries. Defaults to a month
      ago. If no gaId is provided beforehand, then this defaults to site
      creation date.
    endDate: End date for Google Analytics queries. Defaults to today.
    opened: A boolean corresponding to whether the connection is available.
    _retryCount: An integer counting for number of retries; bounded by RETRY_THRESHOLD
    _lastAuthTime: A timestamp indicating time which accessToken was obtained.
    _isEcommerce: A boolean indicating whether or not this Google Analytics
      connection should show ecommerce related things.

  Public Methods:
    listTables: Lists tables; see DataSourceConnection.listTables.
    queryTable: Queries tables; see DataSourceConnection.queryTable.
    getColumnMetadata: Metadata for columns; see DataSourceConnection.geteColumnMetadata.

  Private Methods:
    _checkConnection: Method to check whether current credentials are still valid.
    _initialize: Method to establish the current connection.
    _queryFunc: Helper method for querying.
  """
  def __init__(self, **kwargs):
    super(GAConn, self).__init__()
    self.session      = kwargs.get('session', None)
    self.refreshToken = kwargs['oauth_refresh_token']
    self.accessToken  = None
    self.gaSession    = None
    self.gaId         = str(kwargs['ga_profile_id'])

    self.startDate = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    self.endDate   = datetime.date.today().strftime('%Y-%m-%d')

    # Internal attributes and flags
    self.opened        = False
    self._retryCount   = 0
    self._lastAuthTime = None
    self._isEcommerce  = True

    self._initialize()


  #### Implementation of the DataSourceConnection class


  @retry(2)
  def listTables(self):
    """
    Lists tables for Google Analytics. See DataSourceConnection.listTables for
    more information. Note that the tables for Google Analytics are static, and
    thus are simply returned from a local file.
    """
    if self._isEcommerce:
      return GAParams.getTables()
    else:
      return [t for t in GAParams.getTables() if t['name'] != "Ecommerce"]

  @retry(2)
  def getColumnMetadata(self, tableName, columnExpr, dataType):
    """
    Returns the meta data for a given column. See DataSourceConnection.getColumnMetadata
    for more information. The implementation here runs by constructing a dummy
    Google Analytics query, from which meta data is computed.

    Raises:
      ValueError: Thrown when the connection is not available.
    """
    # TODO: disallow formulas

    columnName = getColumnName(columnExpr['name'], columnExpr['expr'])
    nakedName = columnName[len(tableName)+1:]

    ready = self._checkConnection()
    if ready:
      if nakedName == 'time':
        return { 'min': mktime(strptime(self.startDate, '%Y-%m-%d'))
               , 'max': mktime(strptime(self.endDate, '%Y-%m-%d')) }
      else:
        select = [columnExpr]
        meta = {columnName: {'type': dataType, 'ga': 'metric'}}
        meta['tableName'] = tableName
        #match = re.match(r'ga-(?:dimension|metric)-(.*)', tableName)
        #if match is not None:
        #  tableName = match.group(1)
        #else:
        #  raise ValueError( "dataSources.googleAnalytics.connection.getColumnMetadata: "\
        #                  + "Invalid table name, %s" % tableName)
        t = listDictWithPair(GAParams.getTables(), 'name', tableName)
        gaType = t['meta'][nakedName]['ga']
        if gaType == 'dimension':
          meta[columnName]['ga'] = 'dimension'
          select.append(
            {'name': '[Visitor.visitors]', 'expr': ['ident', {'name': 'Visitor.visitors'}]}
          )
          meta.update({ 'Visitor.visitors': { 'type': 'num'
                                    , 'ga':   'metric'}})
        query = GAQuery( tableName
                       , { 'select' : select
                         , 'meta'   : meta
                         , 'stats'  : {'stats': [], 'groups': []}
                         , 'trans'  : []
                         , 'filter' : {}
                         }
                       , queryFunc = self._queryFunc
                       , startDate = self.startDate
                       , endDate   = self.endDate
                       , gaId      = self.gaId )
        result = query.getData()
        vals = [datum[columnName] for datum in result['data']]
        if dataType == 'cat':
          return { 'values': vals }
        else:
          return { 'min': min(vals)
                 , 'max': max(vals)}
    else:
      raise ValueError( "googleAnalytics.connection.getColumnMetadata"
                      , "Unable to run because not ready.")

  @retry(2)
  def queryTable(self, tableName, querySpec, limit):
    """
    Queries Google Analytics Reporting API and returns the result. See
    DataSourceConnection.queryTable for more information.

    Raises:
      ValueError: Thrown when the connection is not available.
    """
    ready = self._checkConnection()
    if ready:
      query = GAQuery( tableName
                     , querySpec
                     , limit     = limit
                     , queryFunc = self._queryFunc
                     , startDate = self.startDate
                     , endDate   = self.endDate
                     , gaId      = self.gaId )
      return query.getData()
    else:
      raise ValueError("googleAnalytics.connection.queryTable: Unable to run because not ready.")


  #### Helper methods


  def _initialize(self):
    """
    Internal function to obtain all user data. Returns a boolean indicating success.

    Raises:
      Need to raise proper errs.
    """
    try:
      if self.session is not None and 'accessToken' in self.session:
        self.accessToken = self.session['accessToken']
      else:
        self.gaSession   = refreshSession('ga', self.refreshToken, session=self.session)
        self.accessToken = self.gaSession['access_token']
      if self.gaId == '0' or self.gaId == 'None':
        gaAccountInfo = oauthRequest( self.accessToken
                                    , GAParams.getManageUrl())
        gaWebProps    = oauthRequest( self.accessToken
                                    , gaAccountInfo['items'][0]['childLink']['href'])
        gaProfile     = oauthRequest( self.accessToken
                                    , gaWebProps['items'][0]['childLink']['href'])

        self.gaId         = gaProfile['items'][0]['id']
        self.startDate    = gaProfile['items'][0]['created'][0:10] # Site creation date
        self._isEcommerce = gaProfile['items'][0]['eCommerceTracking']

      self._retryCount = 0
      self._lastAuthTime = time()
      self.opened = True
      return self.opened
    except Exception:
      if not self.opened:
        if self._retryCount < RETRY_THRESHOLD: # Hope this works as expected
          self._retryCount += 1
          result = self._initialize()
          self.opened = result
        else:
          self.opened = False
      return self.opened

  def _checkConnection(self):
    """
    Internal method that checks the current credientials are still valid. The
    function checks whether or not the access token has expired. If it has, then
    it shall try to refresh.

    Returns:
      A boolean indicating whether or not the connection is open.
    """
    if self.gaSession:
      if time() - self._lastAuthTime > self.gaSession['expires_in']:
        self.opened = False
        done = self._initialize()
        return done
      else:
        return True
    else:
      self.opened = False
      done = self._initialize()
      return done

  def _queryFunc(self, query):
    """
    A helper function that performs requests.

    Args:
      query: A Google Analytics query object. See dataSources.googleAnalytics.query
        for more information.
    Returns:
      The response from Google Analytics is returned.
    """
    return oauthRequest( self.accessToken
                       , GAParams.getQueryUrl() + urlencode(query))
