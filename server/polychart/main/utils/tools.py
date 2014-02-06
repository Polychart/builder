"""
A collection of very miscellaneous tools.
"""
### Filepath tools
from base64 import urlsafe_b64encode
import atexit
import os

# Ensure tmp directory exists
if not os.path.exists('tmp'):
  os.mkdir('tmp')

def getNewTempFilePath():
  path = os.getcwd() + '/tmp/' + urlsafe_b64encode(os.urandom(18))
  deleteOnExit(path)
  return path

def deleteOnExit(path):
  def cleanup():
    try: os.remove(path)
    except: pass
  atexit.register(cleanup)

### Misc functions
def randomCode():
  # 18 random bytes -- more than a UUID, and looks nicer in base 64
  return urlsafe_b64encode(os.urandom(18))
