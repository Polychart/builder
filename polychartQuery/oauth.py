"""
Module containing parameters and methods shared by OAuth2.0 data sources. See
`/docs/oauth.md` in the same directory for more detailed documentation.
"""
from urllib import urlencode

import requests

try:
  from django.conf import settings
except ImportError:
  settings = object()

REDIRECT_URL = settings.HOST_URL + '/api/data-source/callback'

# OAuth credentials for individual OAuth data sources. These are to be defined
# in the Django settings module that is imported.
OAUTH_CONFIG = {
  'ga': {
    'clientId':       getattr(settings, 'GOOGLE_ANALYTICS_CLIENT_ID', None)
  , 'clientSecret':   getattr(settings, 'GOOGLE_ANALYTICS_CLIENT_SECRET', None)
  , 'authorizeUrl':   "https://accounts.google.com/o/oauth2/auth?"
  , 'accessTokenUrl': "https://accounts.google.com/o/oauth2/token"
  }
}

def oauthRedirect(reqType, name):
  """
  Function that returns the endpoint for the initial OAuth2.0 authentication
  flow.

  Args:
    reqType: Should be 'ga' ('sf' is no longer supported)
    name: The name of the data source connection to be passed into the state.

  Returns:
    A string that is the OAuth2.0 Authentication endpoint for the given request
    type.

  Raises:
    KeyError: Thrown when the reqType is not 'ga'
  """
  if reqType == 'ga':
    loginUrl  = 'https://accounts.google.com/o/oauth2/auth?'
    urlParams = {
      'response_type':   'code'
    , 'scope':           'https://www.googleapis.com/auth/analytics.readonly'
    , 'access_type':     'offline'
    , 'approval_prompt': 'force'
    , 'redirect_uri':    REDIRECT_URL
    , 'client_id':       OAUTH_CONFIG['ga']['clientId']
    , 'state':           'ga-{name}'.format(name=name)}

    return "{base}{params}".format(base=loginUrl, params=urlencode(urlParams))
  else:
    raise KeyError( "oauth.oauthRedirect"
                  , "Invalid reqType, {0}".format(reqType))


def oauthCallback(code, reqType, session=None):
  """
  Function to handle an OAuth2.0 callback.

  Args:
    code: A string representing the OAuth2.0 authentication code provided by the
      target server.
    reqType: Should be 'ga' ('sf' is no longer supported)
    session: A dictionary-like session object. This optional parameter is used to
      store the access token obtained, so it may be used for future requests.

  Returns:
    A dictionary of the authentication response.

  Raises:
    ValueError: Thrown when the request is unsuccessful.

  """
  args = { 'code':          code
         , 'client_id':     OAUTH_CONFIG[reqType]['clientId']
         , 'client_secret': OAUTH_CONFIG[reqType]['clientSecret']
         , 'grant_type':    'authorization_code'
         , 'redirect_uri':  REDIRECT_URL }

  response = requests.post(OAUTH_CONFIG[reqType]['accessTokenUrl'], data=args)

  if response.status_code != 200:
    raise ValueError( "oauth.oauthCallback"
                    , "The request failed with code {code}".format(code=response.status_code))

  result = response.json()
  if session is not None:
    session['accessToken'] = result['access_token']
  return result


def refreshSession(reqType, refreshToken, session=None):
  """
  Function to handle OAuth2.0 refresh token authentication flow. This takes the
  refresh token, makes a request to the corresponding OAuth service provider, and
  obtains a new access token. Generally speaking, the whole response is returned
  since there may be additional information stored there.

  Args:
    reqType: Should be 'ga' ('sf' is no longer supported)
    refreshToken: An OAuth2.0 refreshToken for the request.
    session: A dictionary-like session object. This optional parameter is used to
      store the access token obtained, so it may be used for future requests.

  Returns:
    A dictionary representing the response from the server.

  Raises:
    ValueError: Thrown when the request is unsuccessful.
  """
  args = { 'grant_type':    'refresh_token'
         , 'refresh_token': refreshToken
         , 'client_id':     OAUTH_CONFIG[reqType]['clientId']
         , 'client_secret': OAUTH_CONFIG[reqType]['clientSecret'] }

  response = requests.post(OAUTH_CONFIG[reqType]['accessTokenUrl'], data=args)
  if response.status_code != 200:
    raise ValueError( "oauth.refreshSession"
                    , "The request failed with code {code}".format(code=response.status_code))
  result = response.json()
  if session is not None:
    session['accessToken'] = result['access_token']
  return result

def oauthRequest(accessToken, url, postArgs=None, **kwargs):
  """
  A function to handle a server request in an OAuth2.0 workflow.

  Args:
    accessToken: A string representing a valid OAuth2.0 access token.
    url: A string representing the request url.
    postArgs: An optional dictionary containing arguments for a post request.
    kwargs: Other keyword arguments for url query parameters.

  Returns:
    A dictionary containing the result of the request.

  Raises:
    ValueError: Thrown when the request is unsuccessful.
  """
  if kwargs:
    url += '?' + urlencode(kwargs)

  headers  = {'Authorization': 'Bearer {token}'.format(token=accessToken)}
  response = None
  if postArgs:
    response = requests.post(url, data=postArgs, headers=headers)
  else:
    response = requests.get(url, headers = headers)

  if response.status_code != 200:
    raise ValueError( "oauth.oauthRequest"
                    , "The request failed with status {code}".format(code=response.status_code))

  return response.json()
