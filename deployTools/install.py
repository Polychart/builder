#!/usr/bin/env python2

import errno
import json
import os
import re
import sys

from base64 import b64encode
from getpass import getpass
from shutil import copy2, copytree, rmtree
from subprocess import check_call, check_output

def run():
  showIntro()

  installSystemDeps()
  checkVirtualenvVersion()
  installDir = promptInstallDir()
  setupConfig = determineSetupConfig(installDir)

  installPythonDeps(installDir)

  copyApplicationFiles(installDir)

  writeDjangoConfig(setupConfig, installDir)
  writeGunicornConfig(setupConfig, installDir)

  prepareDatabase(installDir)

  showOutro(installDir)

def showIntro():
  print
  print "Polychart - Lightweight Visual Analytics and Business Intelligence"

def installSystemDeps():
  systemDeps = loadSystemDeps()

  action = showMenu(
    """
Polychart requires the following packages:
%s
    """ % ('\n'.join([" - %s" % p for p in systemDeps])),
    [('quit', "Quit now so that I can install these packages"),
     ('continue', "These packages are installed")]
  )

  if action == 'quit':
    sys.exit(0)

def checkVirtualenvVersion():
  try:
    version = check_output(['virtualenv', '--version'])
  except Exception as err:
    print err
    print """
Virtualenv may not be installed.
Aborting installation.
    """

  match = re.match(r'^v?(\d+)\.(\d+)\.', version)

  if not match:
    # Something weird happened.  We'll just keep going and hope for the best.
    return

  major = int(match.group(1))
  minor = int(match.group(2))

  if major < 1 or (major == 1 and minor < 10):
    print """
Please upgrade virtualenv to at least version 1.10.
Try running the following command:
  sudo pip install -U virtualenv
    """
    sys.exit(1)

def loadSystemDeps():
  with open('system_requirements') as f:
    result = []

    for line in f:
      lineContent = line.split('#')[0].strip()

      if lineContent:
        result.append(lineContent)

    return result

def promptInstallDir():
  defaultDest = os.path.abspath(os.path.join(os.getcwd(), '../../polychart-onprem'))
  result = prompt("Installation directory", defaultDest)
  makeDirectory(result)
  return result

def installPythonDeps(installDir):
  print """
Polychart will now download required Python packages.
  """
  prompt("Press enter to continue")

  vtenvPath = installDir + '/virtualenv'
  if not os.path.exists(vtenvPath + '/bin/activate'):
    check_call(['virtualenv', '--python=python2.7', '--distribute', vtenvPath])

  check_call([vtenvPath + '/bin/pip', 'install', '-r', 'requirements'])

  # TODO Upgrade production deployment to 18.0 and remove this line
  check_call([vtenvPath + '/bin/pip', 'install', 'gunicorn==18.0'])

def determineSetupConfig(installDir):
  setupConfigFilePath = os.path.join(installDir, 'setup_config.json')

  if os.path.exists(setupConfigFilePath):
    print "Detected previous installation.  Upgrading instead."

    return loadSetupConfig(setupConfigFilePath)
  else:
    result = promptSetupConfig()
    writeSetupConfig(result, setupConfigFilePath)
    return result

def loadSetupConfig(path):
  try:
    with open(path) as f:
      return json.load(f)
  except Exception as ex:
    print "Error while identifying previous installation: " + str(ex)
    print "Aborting upgrade."
    sys.exit(1)

def promptSetupConfig():
  result = {
    'secretKey': generateSecretKey(),
    '__IMPORTANT__': [
      "Changes to this configuration file will not take effect",
      "until the Polychart install script is next run.",
    ],
  }

  result['database'] = promptDatabaseConfig()

  print """
What URL will eventually be used to access this instance of Polychart?
Example: https://poly.example.com
  """
  result['hostUrl'] = normalizeHostUrl(prompt("URL"))

  print """
Polychart requires a private TCP port that is protected by a firewall.
we recommend using nginx or apache to forward requests to this
port after completing installation.
  """
  result['internalPort'] = promptNumber("A private TCP port", 0, 65535, 1700)

  return result

def normalizeHostUrl(url):
  return re.match(r'^([a-z]+://.+[^/])/*$', url).group(1)

def promptDatabaseConfig():
  action = showMenu(
    """
Polychart requires a MySQL database installation.

IMPORTANT: This should not be the database that you intend to visualize.
Instead, create an empty database for Polychart.

For example:
  mysql -u root -p
  CREATE DATABASE poly;
    """,
    [('quit', 'Quit now so that I can set up the database'),
     ('continue', 'An empty MySQL database is already set up for Polychart')],
  )

  if action == 'quit':
    sys.exit(0)

  result = {}

  result['ENGINE'] = 'django.db.backends.mysql'
  result['HOST'] = prompt('Database host', default='localhost')
  result['PORT'] = int(prompt('Database port', default='3306'))
  result['USER'] = prompt('Database username', default='root')
  result['PASSWORD'] = prompt('Database password', maskInput=True)
  result['NAME'] = prompt('Database name', default='poly')

  return result

def generateSecretKey():
  return b64encode(os.urandom(64)).replace('/', '').replace('+', '').replace('=', '')

def writeSetupConfig(config, path):
  config['version'] = getSoftwareVersion()
  config['__IMPORTANT__'] = [
    "Changes to this configuration file will not take effect",
    "until the Polychart install script is next run."
  ]

  configJson = json.dumps(config, indent=2)

  with open(path, 'w') as f:
    f.write(configJson)

def getSoftwareVersion():
  with open('version') as f:
    return f.read().strip()

def copyApplicationFiles(installDir):
  print "Copying client files..."
  clientDest = os.path.join(installDir, 'static')
  if os.path.exists(clientDest):
    rmtree(clientDest)
  copytree('static', clientDest)

  print "Copying server files..."
  serverDest = os.path.join(installDir, 'server')
  if os.path.exists(serverDest):
    rmtree(serverDest)
  copytree('server', serverDest)
  copy2('manage.py', installDir)

  makeDirectory(os.path.join(installDir, 'log', 'app'))
  makeDirectory(os.path.join(installDir, 'log', 'gunicorn'))

def writeDjangoConfig(setupConfig, installDir):
  djangoConfigDir = os.path.join(installDir, 'server', 'polychart', 'config')
  deployOverridesPath = os.path.join(djangoConfigDir, 'deployOverrides.py')
  deployParamsPath = os.path.join(djangoConfigDir, 'deployParams.py')

  if not os.path.exists(deployOverridesPath):
    with open(deployOverridesPath, 'w') as f:
      f.write("from polychart.config.deployParams import *\n")

  djangoConfig = {
    'SECRET_KEY': setupConfig['secretKey'],
    'DATABASES': {
      'default': setupConfig['database'],
    },
    'ALLOWED_HOSTS': [
      getDomainFromUrl(setupConfig['hostUrl'])
    ],
    'HOST_URL': setupConfig['hostUrl']
  }

  with open(deployParamsPath, 'w') as f:
    f.write(convertDictToPythonConfig(djangoConfig))

def getDomainFromUrl(url):
  try:
    return re.match(r"^[a-z]+://([^/:]+)", url).group(1)
  except Exception:
    print
    print "Error parsing host URL:"
    print
    raise

def convertDictToPythonConfig(config):
  result = 'import os\n'

  for k, v in config.iteritems():
    result += k
    result += ' = '
    result += json.dumps(v, indent=2)
    result += '\n'

  result += 'STATIC_ROOT = os.path.join(os.path.abspath(os.getcwd()), "static2")\n'
  result += 'STATICFILES_DIRS = (os.path.join(os.path.abspath(os.getcwd()), "static"),)\n'
  return result

def writeGunicornConfig(setupConfig, installDir):
  gunicornConfigPath = os.path.join(installDir, 'gunicorn.conf')
  gunicornConfig = """
from datetime import datetime
from multiprocessing import cpu_count

bind = '127.0.0.1:{}'
workers = 2 * cpu_count() + 1

accesslog = 'log/gunicorn/access_' + datetime.now().strftime('%Y%m%d_%H%M%S')
errorlog = 'log/gunicorn/error_' + datetime.now().strftime('%Y%m%d_%H%M%S')

pythonpath = 'server'

raw_env = ['DJANGO_SETTINGS_MODULE=polychart.config.deploy']
  """.format(setupConfig['internalPort'])

  with open(gunicornConfigPath, 'w') as f:
    f.write(gunicornConfig)

def makeDirectory(path):
  try:
    os.makedirs(path)
  except OSError as err:
    if err.errno != errno.EEXIST:
      raise

def prepareDatabase(installDir):
  print 'Loading database schemas...'
  runDjangoAdminCmd(['syncdb', '--migrate', '--noinput'], installDir)

def runDjangoAdminCmd(args, installDir):
  check_call([installDir + '/virtualenv/bin/python2', 'manage.py'] + args, cwd=installDir)

def showOutro(installDir):
  print """
Thanks for installing Polychart!

To start the application, please change to the install directory:
  %s

and run the following command:
  virtualenv/bin/gunicorn -c gunicorn.conf polychart.wsgi
  """ % (installDir)

def showMenu(pre, items, post=None, promptMsg="Please enter a number"):
  if pre:
    print pre

  for i, (key, description) in enumerate(items):
    print " " + str(i+1) + ". " + description

  if post:
    print post
  else:
    print

  n = promptNumber(promptMsg, 1, len(items))

  return items[n - 1][0] # item key

def promptNumber(msg, start, end, default=None):
  def validator(x):
    try:
      num = int(x)
      return num >= start and num <= end
    except:
      return False

  return int(prompt(msg, validator=validator, default=default))

def prompt(msg, default=None, validator=None, maskInput=False):
  rawMsg = msg
  if default:
    rawMsg += ' [%s]' % default
  rawMsg += ': '

  while True:
    if maskInput:
      x = getpass(rawMsg)
    else:
      x = raw_input(rawMsg)

    x = x.strip()

    if x.lower() in ['exit', 'quit']:
      sys.exit(0)

    if default != None and x == '':
      return default

    if validator == None or validator(x):
      return x

if __name__ == '__main__':
  run()
