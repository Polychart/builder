"""
Module containing view handlers related to data sources
"""
import json
import logging
import urllib

from django.contrib.auth.decorators import login_required
from django.core.cache              import cache
from django.shortcuts               import render, redirect
from django.views.decorators.http   import require_GET, require_POST
from time import time

from polychartQuery.connections       import ( getConnection
                                             , createDataSource
                                             , RedirectRequired )
from polychartQuery.oauth             import   oauthCallback
from polychartQuery.utils             import   saneEncode
from polychart.main.models                        import ( DashboardDataTable
                                                         , DataSource
                                                         , PendingDataSource )
from polychart.main.utils.spec                    import   getDsInfo
from polychart.utils                              import   jsonResponse

#
# View Handlers for Data Sources
#

CACHE_TIMEOUT = 300 # seconds
logger = logging.getLogger(__name__)

@require_POST
@login_required
def dsCreate(request):
  """View Handler for creating data sources."""
  clientDsObj = json.loads(request.body)
  try:
    result = createDataSource(request, clientDsObj)
    if   result['status'] == 'success':
      return jsonResponse({'key': result['key']})
    elif result['status'] == 'error':
      return jsonResponse(result['error'], status = 400)
  except RedirectRequired as red:
    return jsonResponse({'redirect': red.url})

@require_GET
@login_required
def dsCallback(request):
  """View Handler for OAuth2.0 callback."""
  if 'code' not in request.GET or 'state' not in request.GET:
    raise ValueError("Invalid OAuth Response")
  code  = request.GET['code']
  state = request.GET['state']

  reqArgs = state.split('-')
  reqType = reqArgs[0]
  reqName = '-'.join(reqArgs[1:])

  response         = oauthCallback(code, reqType, session = request.session)
  if reqType == 'ga':
    split = reqName.rfind("||")
    response['name'] = reqName[0:split]
    response['gaId'] = reqName[split+2:]
    response['type'] = 'googleAnalytics'

  return render( request
               , 'callback.tmpl'
               , dictionary = { 'response': saneEncode(response)}
               )

@require_GET
@login_required
def dsList(request):
  """View Handler to list data sources."""
  # pylint: disable = E1101
  # Pylint does not recognize Django models as having 'objects' attribute.
  dataSources = DataSource.objects.filter(user=request.user)

  result = [
      { 'key':  ds.key
      , 'name': ds.name
      , 'type': ds.type
      } for ds in dataSources]

  return jsonResponse({'dataSources': result})

@require_POST
@login_required
def dsDelete(request, dsKey):
  """View Handler to delete data sources."""
  # pylint: disable = E1101
  # Pylint does not recognize Django models as having 'objects' attribute.
  ds = DataSource.objects.get(key=str(dsKey), user=request.user)

  # Avoid leaving behind broken data sources
  refs = DashboardDataTable.objects.filter(data_source=ds)
  dashs = []
  for r in refs:
    if r.dashboard not in dashs:
      dashs.append(r.dashboard)
  refs.delete()
  for dash in dashs:
    dash.delete()

  ds.delete()

  return jsonResponse({})

#
# View Handlers related to tables
#

def runConnectionMethod(conn, methodName, *args):
  startTime = time()
  cacheKey = conn.generateCacheKey(methodName, args)
  cachedResult = cache.get(cacheKey)
  if cachedResult:
    logger.info('Cache hit took {sec}s'.format(sec=time()-startTime))
    return cachedResult

  result = getattr(conn, methodName)(*args)

  startTime = time()
  cache.set(cacheKey, result, CACHE_TIMEOUT)
  logger.info('Cache save took {sec}s'.format(sec=time()-startTime))

  return result

@require_POST
def tableList(request, dsKey):
  """View Handler for listing tables in a dashboard."""
  connection = getConnection(request, dsKey)
  tables     = runConnectionMethod(connection, 'listTables')
  return jsonResponse(saneEncode(tables))

@require_POST
def tableMeta(request, dsKey):
  """View Handler for returning table meta data."""
  tableName  = request.POST.get('tableName', None)
  columnExpr = json.loads(urllib.unquote(request.POST.get('columnExpr', None)))
  dataType   = request.POST.get('type', None)
  if None in [tableName, columnExpr, dataType]:
    raise ValueError("views.dataSource.tableMeta",
                     "Invalid request; missing data.")
  try:
    connection = getConnection(request, dsKey)
    result     = runConnectionMethod(
      connection,
      'getColumnMetadata',
      tableName,
      columnExpr,
      dataType
    )
  except ValueError as err:
    if len(err.args) > 0:
      return jsonResponse({'message': str(err.args[0])}, status=500)
    return jsonResponse({'message': None}, status=500)
  return jsonResponse(saneEncode(result))

@require_POST
def tableQuery(request, _):
  """View Handler for performing a query on a table."""
  spec = json.loads(urllib.unquote(request.POST.get('spec', None)))
  assert spec, "Invalid query specification!"

  tableName, dsKey = getDsInfo(spec)[0]
  limit            = int(request.POST.get('limit', 1000))
  try:
    connection = getConnection(request, dsKey)
    result     = runConnectionMethod(
      connection,
      'queryTable',
      tableName,
      spec,
      limit
    )
  except ValueError as err:
    if len(err.args) > 0:
      return jsonResponse({'message': str(err.args[0])}, status=500)
    return jsonResponse({'message': None}, status=500)
  return jsonResponse(result) #saneEncoded already in queryTable

#
# View Handlers related to pending datasources.
#

@require_POST
def dsPendingCreate(request):
  """View Handler for creating pending datasources."""
  dataSourceParamsJson = json.loads(request.body)
  pendingDs = PendingDataSource(params_json=dataSourceParamsJson)
  pendingDs.save()

  return jsonResponse({'key': pendingDs.key})

@require_GET
@login_required
def dsPendingVerify(request, pendingDsKey):
  """View Handler to verify pending data source creation."""

  result = _verifyPendingDs(request, pendingDsKey)

  if result['status'] == 'success':
    return redirect('/home?newDataSourceKey=' + urllib.quote(result['dsKey']))
  elif result['status'] == 'notFound':
    return redirect('/home')
  else:
    return render( request
                 , 'verifyPendingDataSource.tmpl'
                 , dictionary = { 'result': result }
                 )

@require_POST
def dsPendingDelete(request, pendingDsKey):
  # user may be null, this is acceptable
  pds = PendingDataSource.objects.get(key=str(pendingDsKey), user=request.user)

  pds.delete()

  return jsonResponse({'status': 'success'})

def _verifyPendingDs(request, pendingDsKey):
  """
  Helper function to verify pending data source creation.

  Args:
    request: A Django request object; used for secureStorageKey and sessionKey.
    pendingDsKey: A data source key corresponding to the one needing verification.

  Returns:
    A dictionary detailing whether or not the verification was a success or failure.

    In the case of success, the 'status' field of the return dictionary is 'success',
    and the data source key is passed back in the 'dsKey' field.

    In the case of failure, the 'status' field is set to 'error' and a 'error' field
    is filled with a description of the error.

    In the special case that the data source was not found, the 'status' field has
    value 'notFound'.
  """
  # pylint: disable = E1101
  # Pylint does not recognize Django models as having 'objects' attribute.
  # Pylint does not recognize Django model as having 'DoesNotExist' attribute.
  try:
    pendingDs = PendingDataSource.objects.get(key=pendingDsKey)
  except PendingDataSource.DoesNotExist:
    return {'status': 'notFound'}

  if pendingDs.user:
    assert pendingDs.user == user

  dsParams = pendingDs.params_json
  result = createDataSource(request, dsParams)

  if result['status'] == 'success':
    # Move over the local data source object, if it exists
    try:
      lds = LocalDataSource.objects.get(pendingdatasource=pendingDs)
      lds.datasource = DataSource.objects.get(key=result['key'])
      lds.pendingdatasource = None
      lds.save()
    except LocalDataSource.DoesNotExist:
      pass
    return { 'status': 'success'
           , 'dsKey': result['key']}

  if result['status'] == 'error':
    return { 'status': 'error'
           , 'error': result['error']}

  raise Exception('unknown createDs status: ' + result['status'])
