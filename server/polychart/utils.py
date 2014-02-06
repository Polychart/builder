"""
A pleasant of assortment of functions facilitating the use of Django.
"""

import json

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import RedirectView, TemplateView

from polychart.main.models import UserInfo

def templateContextProcessor(context):
  """
  Adds global variables to all templates in the project.
  Avoids needing to pass in the same values each time a template is rendered.
  """

  result = {
    'settings': settings
  }

  if context.user.is_authenticated():
    result['userInfo'] = UserInfo.objects.get(user=context.user)

  return result

def jsonResponse(data, status=200):
  """
  Takes data and returns an HttpResponse object that is tagged JSON

  Args:
    data: Any serializable data.
    status: Optional status for the HttpResponse object. By default, the status
      is assumed to be 200 (successful).

  Returns:
    HttpResponse object that has header line "Content-Type: application/json",
    and the passed in data as a JSON blob.
  """
  return HttpResponse( json.dumps(data)
                     , content_type = 'application/json'
                     , status = status)

def template(templateName):
  """
  Simple shortcut for indicating in a Django routing file that a template
  should be rendered.
  """
  return TemplateView.as_view(template_name=templateName)

def permanentRedirect(targetUrl):
  """
  Simple shortcut for indicating a 301 redirect in a Django routing file.
  """
  return RedirectView.as_view(url=targetUrl, permanent=True)

def temporaryRedirect(targetUrl):
  """
  Simple shortcut for indicating a 302 redirect in a Django routing file.
  """
  return RedirectView.as_view(url=targetUrl, permanent=False)
