"""
Django handlers to deal with SSH datasource connections.
"""
import json
import logging
import os
import subprocess

from django.contrib.auth.decorators import login_required
from django.views.decorators.http   import require_POST

from polychart.main.utils.tools import getNewTempFilePath, deleteOnExit
from polychart.utils            import jsonResponse

import polychart.main.utils.validate as validate # filepath, linuxUsername, hostname

@require_POST
@login_required
def sshKeygen(request):
  keyFilePath = getNewTempFilePath()
  subprocess.check_output(
    [ 'ssh-keygen'
    , '-q'
    , '-t', 'rsa'
    , '-f', keyFilePath
    , '-N', ''
    , '-C', 'polychart'
    ])

  with open(keyFilePath) as f:
    privateKey = f.read()
  with open(keyFilePath + '.pub') as f:
    publicKey = f.read()
  deleteOnExit(keyFilePath + '.pub')

  return jsonResponse({'privateKey': privateKey, 'publicKey': publicKey})

@require_POST
@login_required
def sshFileExists(request):
  clientDsObj = json.loads(request.body)

  username   = clientDsObj['username']
  host       = clientDsObj['host']
  port       = int(clientDsObj['port'])
  privateKey = clientDsObj['privateKey']
  filePath   = clientDsObj['filePath']
  socket     = bool(clientDsObj.get('isSocket', False))

  if not validate.linuxUsername(username):
    return jsonResponse({'status': 'connFailed', 'invalidField': 'username'})

  if not validate.hostname(host):
    return jsonResponse({'status': 'connFailed', 'invalidField': 'host'})

  if not validate.filepath(filePath):
    return jsonResponse({'status': 'connFailed', 'invalidField': 'filePath'})

  # 0600 permissions required by ssh
  keyPath = getNewTempFilePath()
  with os.fdopen(os.open(keyPath, os.O_WRONLY | os.O_CREAT, 0600), 'w') as f:
    f.write(privateKey)

  def runRemoteCmd(cmd):
    return subprocess.call(
      [ 'ssh'
      , '-2'
      , '-o', 'StrictHostKeyChecking=no'
      , '-o', 'PasswordAuthentication=no'
      , '-p', str(port)
      , '-i', keyPath
      , '%s@%s' % (username, host)
      , cmd
      ])

  if runRemoteCmd('echo -n') != 0:
    return jsonResponse({'status': 'connFailed'})

  if socket: fileTypeTest = 'S'
  else:      fileTypeTest = 'f'

  if runRemoteCmd('test -%s "%s"' % (fileTypeTest, filePath)) != 0:
    return jsonResponse({'status': 'notFound'})
  else:
    return jsonResponse({'status': 'found'})

