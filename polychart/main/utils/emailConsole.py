from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage, EmailMultiAlternatives

import json
import logging
import urllib2

logger = logging.getLogger(__name__)

class ConsoleEmailBackend(BaseEmailBackend):
  """
  Django email backend that simply logs emails to console for debugging
  """

  def send_messages(self, email_messages):
    if not email_messages:
      return

    for message in email_messages:

      content = {}
      if isinstance(message, EmailMessage):
        content["text/%s" % message.content_subtype] = message.body

      if isinstance(message, EmailMultiAlternatives):
        for alt in message.alternatives:
          content[alt[1]] = alt[0]

      output = '''
----------------------------------------
Redirecting email to log.

From: %s
To: %s
Bcc: %s
Subject: %s
''' % (
        repr(message.from_email),
        repr(message.to),
        repr(message.bcc),
        repr(message.subject),
      )
      for n, v in message.extra_headers.items():
        output += '%s: %s\n' % (n, repr(v))
      for contentType, content in content.items():
        output += '\n'
        output += '-- Email body as %s --\n' % contentType
        output += content
        output += '\n'
        output += '-- End of email body as %s --\n' % contentType
      output += '-' * 40
      output += '\n'
      logger.info(output)
