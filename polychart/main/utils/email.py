import datetime
import hashlib
import json
import logging

import django.core.mail
from django.contrib.auth.models import User

FROM_ADDR = 'The Polychart Team <admin@polychart.com>'

logger = logging.getLogger(__name__)

# Tim thinks that you probably want this function:
def sendEmail(subject, body, toAddr, fromAddr=FROM_ADDR, params=None):
  if params is not None:
    paramsJson = json.dumps(params)
  else:
    paramsJson = ''

  success = False
  message_hash = ''
  try:
    subject = unicode(subject.format(**params), 'utf-8')
    body    = unicode(body.format(**params), 'utf-8')
    django.core.mail.send_mail(subject, body, fromAddr, [toAddr])
    success = True
  except Exception:
    logger.exception('Error sending email')
  finally:
    # create email history.
    try:
      m = hashlib.md5()
      m.update(body.encode('utf-8'))
      message_hash = m.hexdigest()[:8]
      logger.info( "Sent email with subject '%s' to %s. Hash: %s, success: %s, params: %s"
                 , subject
                 , toAddr
                 , message_hash
                 , success
                 , paramsJson
                 )
    except Exception:
      logging.exception('Error while logging email')

# Luc thinks that you might also be interested in this function:
def sendEmailAsync(subject, body, toAddr, fromAddr=FROM_ADDR, params=None):
  from threading import Thread
  Thread(
    target=sendEmail,
    args=(subject, body, toAddr),
    kwargs=dict(fromAddr=fromAddr, params=params)
  ).start()
