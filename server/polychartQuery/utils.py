"""
Miscellaneous functions used throughout the code base.
"""
from base64 import urlsafe_b64encode

import atexit
import os
import dateutil
import re

# listDictWithPair : [Dict] -> Key -> Value -> Dict
# Given a list of dictionaries, find dictionary with given (key, value) pair.
def listDictWithPair(dictList, key, value):
  for d in dictList:
    if key in d and d[key] == value:
      return d
  return None

#### File path tools
if not os.path.exists('tmp'):
  os.mkdir('tmp')

def getNewTempFilePath():
  path = os.getcwd() + '/tmp/' + urlsafe_b64encode(os.urandom(18))
  def cleanup():
    try:
      os.remove(path)
    except:
      pass
  atexit.register(cleanup)
  return path

### Functions to sanitize data
### NOTE: To be deprecated as the codebase moves to Python 3.*
def saneEncode(obj):
  """
  An unfortunate function whose job is to deal with the unpleasant feud between
  unicode strings and bytecode strings in Python 2.*.

  NOTE: This function is to be deprecated if and when the codebase shifts to
  Python 3.*.

  Args:
    obj: Any object that needs to be encoded into a string; mainly used when
      passing data back to the client side.

  Returns:
    A bytestring representing the original object.
  """
  if type(obj) == list:
    return [saneEncode(item) for item in obj]
  elif type(obj) == dict:
    return {str(key): saneEncode(obj[key]) for key in obj}
  else:
    return tryParse(obj)

def tryParse(blob):
  """
  Another rather unfortunate function whose duty is to make sure no type
  information is lost during the encoding process. This function, like its poor
  sibling `saneEncode` should be deprecated upon moving to Python 3.*.

  Args:
    blob: Some object to be parsed.

  Returns:
    Depending on the real type of blob, a data value that is in, hopefully, the
    correct type. If nothing good is found, a string is returned.
  """
  if type(blob) is int:
    return int(blob)
  elif type(blob) is float:
    return float(blob)

  try:
    return int(blob)
  except ValueError:
    pass
  try:
    return float(blob)
  except ValueError:
    pass
  # Note: a "catch-all" date check fails here because some strings that are 
  # not representing dates gets mistaken as dates: e.g. "" and "AD"
  return normalizeStrings(blob)

QUOTE_REGEX = re.compile(r'^u?(\'|\")(.*)\1$')
def normalizeStrings(string):
  """
  Yet another member to the poor family of functions dealing with custodial work
  in regards to data. This function strips unnecessary quotations and 'u'
  characters preceding strings marking that it is a unicode string.

  Args:
    string: A string to be cleaned.

  Returns:
    A string that will hopefully lack extraneous quotation marks and the
    prefixing 'u' character for unicode strings.
  """
  # Decode/encode  utf8 and ignore all errors; this is to prevent errors when
  # we're later calling json.dumps()
  # (doing both since different db's return strings in different encodings)
  try:
    string = str(string)
  except:
    pass
  try:
    string = string.decode('utf-8', errors='ignore')
  except:
    pass
  try:
    string = string.encode('utf-8', errors='ignore')
  except:
    pass

  try:
    while True:
      string, matches = QUOTE_REGEX.subn(r'\2', string)
      if matches == 0:
        break
    return string
  except:
    return string

def isNumber(x):
  try:
    float(x)
    return True
  except:
    return False

def unbracket(name, expr):
  """
  Method to get the unbracketed name of an expression

  Args:
    name: The fully bracketed name
    expr: The column expression associated with the name

  Returns:
    The unbracketed form of the name. e.g. --
      [column]      =>  column
      [col1]+[col2] =>  [col1]+[col2]
      sum([column]) =>  sum([column])
  """
  tag, fields = expr
  if tag == 'ident':
    return fields['name']
  return name

def getColumnName(name, expr):
  """
  Method to get the unbracketed name of an expression

  Args:
    name: The fully bracketed name
    expr: The column expression associated with the name

  Returns:
    The unbracketed form of the name, no formulas allowed
  """
  tag, fields = expr
  if tag == 'ident':
    return fields['name']
  raise ValueError("Formulas are not allowed!")

