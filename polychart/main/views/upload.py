"""
Module to deal with uploading data.
"""
import json
import os

from django.contrib.auth.decorators import login_required
from django.views.decorators.http   import require_POST

from polychart.main.models          import LocalDataSource, PendingDataSource
from polychart.main.utils.csvParser import parseForPolychart, parseForPreview
from polychart.utils                import jsonResponse

@require_POST
@login_required
def getKey(request):
  """
  Provides a key to upload to. This structure will be useful if/when we enable
  chunking of uploads. If data contains a key already, we're uploading a new
  version of the dataset. This functionality is unused for the moment.
  """
  # pylint: disable = E1101
  # Pylint does not notice Django model attributes.
  user = request.user
  data = json.loads(request.body)
  pds  = PendingDataSource.objects.create(user = user, params_json = data)
  if 'key' in data:
    try:
      lds = LocalDataSource.objects.get(user=user, datasource__key=data['key'])
      lds.pendingdatasource = pds
      lds.save()
    except LocalDataSource.DoesNotExist:
      pass
  pds.params_json['key'] = pds.key
  pds.save()

  return jsonResponse({'key': pds.key})

@require_POST
@login_required
def postFile(request, pdsKey, index='0'):
  """
  Handler to upload data. Validates the key and index, and dumps the raw content
  of the request to a file.
  """
  # pylint: disable = E1101
  # Pylint does not notice Django model attributes.
  user = request.user

  # Ensure the table index is numeric
  if not index.isdigit():
    return jsonResponse({'status': 'error', 'error': 'Invalid table index: ' + index})

  # Ensure the key is valid to prevent a malicious user from
  # trying to write to 'uploadedData/raw/../../foo'
  pds = PendingDataSource.objects.get(key=str(pdsKey), user=user)

  if not os.path.exists('uploadedData/raw/'):
    os.makedirs('uploadedData/raw/')
  with open("uploadedData/raw/%s-%s" % (pds.key, index), 'wU') as f:
    f.write(request.body)

  return jsonResponse({'status': 'success'})

@require_POST
@login_required
def previewCsv(request, key, index='0'):
  """
  Handler to get a preview of an uploaded file. This preview is shown to the
  user using SlickGrid in order to verify that the file is being parsed
  correctly.
  """
  # pylint: disable = E1101
  # Pylint does not notice Django model attributes.
  user = request.user

  data = json.loads(request.body)

  # Ensure the table index is numeric
  if not index.isdigit():
    return jsonResponse({'status': 'error', 'error': 'Invalid table index: ' + index})

  pds = PendingDataSource.objects.get(key=str(key), user=user)

  with open("uploadedData/raw/%s-%s" % (pds.key, index), 'rU') as f:
    parsed = parseForPreview(f, data)
    return jsonResponse(parsed)

@require_POST
@login_required
def cleanCsv(request, key):
  """
  Handler to clean uploaded CSV data. Unlike previewCsv, this function expects a
  parsing config for all of the tables. It parses each in turn, and dumps the
  whole list into the database in JSON format.
  """
  # pylint: disable = E1101
  # Pylint does not notice Django model attributes.
  user = request.user

  data = json.loads(request.body)

  pds = PendingDataSource.objects.get(key=str(key),user=user)
  (lds, _) = LocalDataSource.objects.get_or_create(pendingdatasource=pds)

  lds.json = []

  for index, format in enumerate(data['tables']):
    with open("uploadedData/raw/%s-%s" % (pds.key, index), 'rU') as f:
      lds.json.append(parseForPolychart(f, format))

  lds.save()

  return jsonResponse({'status': 'success'})
