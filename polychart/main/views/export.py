"""
View Handlers and functions for exporting dashboards. See the README located in
`/exportService/` for more information on how this works.
"""
import json
import websocket

from django.conf                  import settings
from django.views.decorators.http import require_GET, require_POST
from django.http                  import HttpResponse
from urllib                       import urlencode, unquote

from polychartQuery.connections   import getConnection
from polychart.main.utils.spec    import getDsInfo
from polychart.main.utils.svg     import constructSvg, GRID_SIZE
from polychart.main.utils.tools   import randomCode
from polychart.utils              import jsonResponse

@require_POST
def dashExportCode(request):
  """
  Handler function to produce session code so that the user may be redirected to
  a unique URL for the export task to take place.

  Args:
    request: Django request object; should contain the serialized dashboard
      specification in request.POST.

  Returns:
    A unique code corresponding to the key used to store the POST data in the
    request session object.
  """
  if not settings.EXPORT_SERVICE_PORT:
    raise ValueError('Received an export request, but exporting is not enabled')

  exportRequest = json.loads(request.body)
  serial     = exportRequest['serial']
  exportType = exportRequest['exportType']
  code       = randomCode()

  request.session[code] = { 'serial':     serial
                          , 'exportType': exportType}
  return jsonResponse({'code': code})

@require_GET
def dashExport(request, code):
  """
  Handler function to export dashboard to SVG, PDF, or PNG.

  Args:
    request: Django request object.
    exportType: A string corresponding to the format for export.
    code: A code to identify the serialized data stored in the session field of
      the Django request.

  Returns:
    A file that corresponds to the dashboard encoded by `serial`, in the format
    requested.

  Raises:
    ValueError: Thrown when an invalid export type is passed in.
  """
  if not settings.EXPORT_SERVICE_PORT:
    raise ValueError('Received an export request, but exporting is not enabled')

  data       = request.session[code]
  serial     = data['serial']
  exportType = data['exportType']

  svg = _getSvg(request, serial)
  res, contentType = None, None

  if   exportType == 'svg':
    res = svg
    contentType = "image/svg+xml"
  else:
    import cairosvg
    # pylint: disable = E1101
    # Pylint does not recognize svg2pdf/svg2png method in cairosvg
    if exportType == 'pdf':
      res = cairosvg.svg2pdf(svg)
      contentType = "application/pdf"
    elif exportType == 'png':
      res = cairosvg.svg2png(svg)
      contentType = "image/png"
    else:
      raise ValueError("views.export.dashExport: Invalid export format, %s" % exportType)

  response = HttpResponse(res, content_type=contentType)
  response['Content-Disposition'] = "attachment;filename=dashboard." + exportType
  return response

#### Helper methods for rendering

def _getSvg(request, serial):
  """
  Helper method to transform a raw dashboard builder serialized state to an SVG
  image.

  Args:
    request: A Django request object; used for data source querying in the
      build process.
    serial: A raw dashboard builder serialized dictionary.

  Returns:
    An SVG image corresponding to the serialized state passed in.
  """
  if type(serial) is str:
    dashItems = json.loads(serial)
  else:
    dashItems = serial
  rawJS, procSerial = [], []
  for item in dashItems:
    if item['itemType'] in ['ChartItem', 'NumeralItem', "PivotTableItem"]:
      rawJS.append(item)
    else:
      procSerial.append(item)
  js = _processJS(request, rawJS)
  procSerial += js
  procSerial = sorted(procSerial, key=(lambda s: s['zIndex']))
  svg = constructSvg(procSerial)
  return svg

def _processJS(request, rawJS):
  """
  Helper function to produce a scene tree for each abstract js spec.

  Args:
    request: Django  request object; used to make data queries to plot charts.
    rawJS: A list of Polychart2.js chart or numeral specifications.

  Returns:
    A list of scene trees that can be made into SVG elements. These scene trees
    are in the form of a list of dictionaries. These dictionaries have keys
    that specify an SVG attribute and the value specifies the associated value.
  """
  rendered = []
  for js in rawJS:
    ws = websocket.create_connection("ws://localhost:%s/" % settings.EXPORT_SERVICE_PORT)
    js['spec']['width']  = js['position']['width'] * GRID_SIZE
    js['spec']['height'] = js['position']['height'] * GRID_SIZE
    ws.send(urlencode({ 'type': 'spec'
                      , 'spec': json.dumps(js['spec']) }))
    if js['itemType'] == 'NumeralItem':
      spec   = json.loads(unquote(ws.recv()))
      result = _getData(request, spec)
      ws.send(urlencode({ 'type':     'queryData'
                        , 'numeral':  True
                        , 'blob':     json.dumps(result) }))
      renderedSpec    = ws.recv()
      renderedNumeral = _getRendered('NumeralItem', renderedSpec, js)
      rendered.append(renderedNumeral)
    elif js['itemType'] == 'ChartItem':
      for _ in js['spec']['layers']:
        spec   = json.loads(unquote(ws.recv()))
        result = _getData(request, spec)
        ws.send(urlencode({ 'type':   'queryData'
                          , 'layer':  spec['layer']
                          , 'blob':   json.dumps(result)
                          }))
        renderedSpec  = ws.recv()
        renderedChart = _getRendered('ChartItem', renderedSpec, js)
        rendered.append(renderedChart)
    elif js['itemType'] == 'PivotTableItem':
      spec   = json.loads(unquote(ws.recv()))
      result = _getData(request, spec)
      ws.send(urlencode({ 'type':   'queryData'
                        , 'table':  True
                        , 'blob':   json.dumps(result) }))
      renderedSpec  = ws.recv()
      renderedChart = _getRendered('PivotTableItem', renderedSpec, js)
      rendered.append(renderedChart)
    ws.close()
  return rendered

def _getData(request, spec):
  """
  Helper function to query for data.

  Args:
    request: A Django request object; for querying tables.
    spec: A data spec object. See 'abstract.DataSourceConnection.queryTable' for
      more details.

  Returns:
    A dictionary with fields 'data' and 'meta' representing a Polychart2.js formatted
    data object.
  """
  tableName, dsKey = getDsInfo(spec)[0]
  connection       = getConnection(request, dsKey)
  return connection.queryTable(tableName, spec, 1000)

def _getRendered(itemType, renderedObj, dashSpec):
  """
  Helper function to get rendered object from Node.js server.

  Args:
    itemType: The type of specification that is being recieved; expected to be
      either 'ChartItem' or 'NumeralItem'.
    renderedObj: A dictionary resulting from rendering the object on the Node.js
      server. Will begin with field 'items', which has an array of dictionaries.
    dashSpec: A dashboard builder serialized state.

  Returns:
    An abstract scene representation of the 'renderedObj' initially passed in.
    Will be a dictionary of the following form:

      { itemType: 'ChartItem' (or 'NumeralItem')
      , items: [...]
      , zIndex: 23
      , position: { top: 12
                  , left: 5
                  , width: 6
                  , height: 8}
      , gridSize: 25}

  Raises:
    ValueError: Thrown when itemType is neither 'ChartItem' nor 'NumeralItem'.
  """
  if itemType not in ['ChartItem', 'NumeralItem', "PivotTableItem"]:
    raise ValueError("views.export._getRendered", "Invalid item type, %s" % itemType)
  jsScene = json.loads(renderedObj)
  jsScene.update({ 'itemType': itemType
                 , 'position': dashSpec['position']
                 , 'zIndex':   dashSpec['zIndex']
                 , 'gridSize': GRID_SIZE })
  return jsScene
