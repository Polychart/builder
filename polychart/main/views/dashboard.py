"""
Django handler functions for dashboards.
"""
import json

from django.contrib.auth.decorators import login_required
from django.http                    import Http404
from django.shortcuts               import render, redirect
from django.views.decorators.http   import require_GET, require_POST

from polychart.main.models        import ( Dashboard
                                         , DashboardDataTable
                                         , DataSource
                                         , LocalDataSource )
from polychartQuery.utils         import saneEncode
from polychart.utils              import jsonResponse

### Helper functions to deal with models
def createTableRefs(dash, dataCollection):
  for filteredDataSource in dataCollection:
    dsKey = str(filteredDataSource['dataSourceKey'])
    dataSource = DataSource.objects.get(key=dsKey, user=dash.user)
    for tableName in list(filteredDataSource['tableNames']):
      DashboardDataTable(
        dashboard=dash,
        data_source=dataSource,
        table_name=str(tableName)
      ).save()

def deleteTableRefs(dash):
  DashboardDataTable.objects.filter(dashboard=dash).delete()

localDataSourceTypes = ['csv']

### Dashboard Handlers

@require_GET
@login_required
def dashShow(request, dashKey, action):
  dash = Dashboard.objects.get(key=str(dashKey), user=request.user)
  tableRefs = DashboardDataTable.objects.filter(dashboard=dash)

  tableNameMap = {}
  for tableRef in tableRefs:
    dsKey = tableRef.data_source.key
    if dsKey in tableNameMap:
      tableNameMap[dsKey].append(tableRef.table_name)
    else:
      tableNameMap[dsKey] = [tableRef.table_name]

  data = DataSource.objects.get(key=dsKey)

  if data.type in localDataSourceTypes:
    tables = LocalDataSource.objects.get(datasource__key=dsKey).json
    dataCollection = [
      { 'type':          'local'
      , 'dataSourceKey': dsKey
      , 'dataSourceType':data.type
      , 'tableNames':    [table['name'] for table in tables]
      , 'tables':        tables
      }
    ]
  else:
    dataCollection = [
      { 'type':          'remote'
      , 'dataSourceKey': dsKey
      , 'tableNames':    tableNames
      , 'dataSourceType':data.type
      } for dsKey, tableNames in tableNameMap.items()
    ]

  if action in ['edit', 'view']:
    return render( request
                 , { 'edit': 'dashEdit.tmpl'
                   , 'view': 'dashView.tmpl'
                   }[action]
                 , dictionary = { 'name':           dash.name
                                , 'key':            dash.key
                                , 'dataCollection': json.dumps(dataCollection)
                                , 'dashboardSpec':  json.dumps(json.loads(dash.spec_json))
                                }
                 )
  else:
    raise Http404

@require_POST
@login_required
def dashCreate(request):
  clientDbObj = json.loads(request.body)

  dash = Dashboard( name      = str(clientDbObj['name'])
                  , spec_json = json.dumps(clientDbObj['spec'])
                  , user      = request.user
                  )
  dash.save()

  createTableRefs(dash, list(clientDbObj['dataCollection']))

  return jsonResponse({'key': dash.key})

@require_GET
@login_required
def dashList(request):
  dashboards = Dashboard.objects.filter(user=request.user)
  result = [{'key': dash.key, 'name': dash.name} for dash in dashboards]

  return jsonResponse({'dashboards': result})

@require_POST
@login_required
def dashUpdate(request, dbKey):
  redirectUrl = None
  clientDashObj = {}

  if request.META['CONTENT_TYPE'] and request.META['CONTENT_TYPE'].startswith("multipart"):
    clientDashObj = json.loads(request.POST['data'][0])
    redirectUrl = request.POST['redirect'][0]
  else:
    clientDashObj = json.loads(request.body)


  dash = Dashboard.objects.get(key=str(dbKey), user=request.user)

  if 'name' in clientDashObj:
    dash.name = str(clientDashObj['name'])
  dash.spec_json = json.dumps(clientDashObj['spec'])
  dash.save()

  deleteTableRefs(dash)
  createTableRefs(dash, list(clientDashObj['dataCollection']))

  if redirectUrl: return redirect(redirectUrl)
  else:           return jsonResponse({})

@require_POST
@login_required
def dashDelete(request, dbKey):
  dash = Dashboard.objects.get(key=str(dbKey), user=request.user)
  deleteTableRefs(dash)
  dash.delete()

  return jsonResponse({})
