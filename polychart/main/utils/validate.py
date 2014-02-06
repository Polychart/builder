"""
Collection of utility functions for validation of various sorts.
"""
import re

def filepath(path):
  """
  Function to validate file paths.

  Args:
    path: A string representing a filepath.
  Returns:
    Boolean corresponding to success of validation.
  """
  return _validateWithRegex(100, r'[a-zA-Z0-9_./][a-zA-Z0-9_\-./]*', path)

def linuxUsername(username):
  """
  Function to validate Linux system usernames.

  Args:
    username: A string representing a Linux username.
  Returns:
    Boolean corresponding to success of validation.
  """
  return _validateWithRegex(32, r'[a-zA-Z_][a-zA=Z0-9_\-.]*', username)

def hostname(host):
  """
  Function to validate external hostnames.

  Args:
    host: A string representing a hostname.
  Returns:
    Boolean corresponding to success of validation.
  """
  return _validateWithRegex(255, r'[a-zA-Z0-9_][a-zA-Z0-9_\-.]*', host)

### Helper functions

def _validateWithRegex(maxLength, pattern, inputStr):
  """
  Internal function to define validation methods with a regular expression.

  Args:
    maxLength: Integer denoting the maximum possible length of input string.
    pattern: A Python Regex expression to execute.
    inputString: The string that is to be validated.

  Returns:
    A boolean corresponding to whether or not the validation succeded is returned.
  """
  if len(inputStr) > maxLength:
    return False
  match = re.match(pattern, inputStr)
  return match.group(0) == inputStr
