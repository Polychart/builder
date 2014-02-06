from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage, EmailMultiAlternatives

import urllib2
import json

class EmailError(Exception):
  def __init__(self, errors):
    Exception.__init__(self, errors)
    self.errors = errors

class PostageappEmailBackend(BaseEmailBackend):

  def __init__(self, fail_silently=False, **kwargs):
    self.fail_silently = fail_silently
    self.postageapp_endpoint = "https://api.postageapp.com/v.1.0/send_message.json"

    if not getattr(settings, "EMAIL_POSTAGEAPP_API_KEY"):
      raise ImproperlyConfigured("You need to provide EMAIL_POSTAGEAPP_API_KEY in your Django settings file.")

  def send_messages(self, email_messages):

    if not email_messages:
      return
    errors = []

    for message in email_messages:

      content = {}
      if isinstance(message, EmailMessage):
        content["text/%s" % message.content_subtype] = message.body

      if isinstance(message, EmailMultiAlternatives):
        for alt in message.alternatives:
          content[alt[1]] = alt[0]

      message_dict = {
        'api_key': getattr(settings, "EMAIL_POSTAGEAPP_API_KEY"),
        'arguments': {
          'recipients': message.to,
          'headers': {
            "subject": message.subject,
            "from": message.from_email,
            "bcc": message.bcc,
          },
          'content': content,
        }
      }

      if getattr(message, "extra_headers"):
        message_dict["arguments"]["headers"].update(message.extra_headers)

      try:
        req = urllib2.Request(self.postageapp_endpoint, json.dumps(message_dict), {'Content-Type': 'application/json'})
        response = urllib2.urlopen(req)

      except urllib2.HTTPError, e:
        jsonobj = None
        try: jsonobj = json.loads(e.read())
        except Exception, e: pass

        if jsonobj is not None: errors.append(jsonobj)
        else: errors.append('Unknown Error')

    if not self.fail_silently and errors:
      raise EmailError(errors)
