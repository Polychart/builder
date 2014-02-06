"""
Django Model definitions used in polychart.com
"""
from datetime import date

import django.utils.timezone
import hashlib
import hmac
import os
import urllib

from base64                     import urlsafe_b64encode
from django.conf                import settings
from django.contrib.auth.models import User
from django.core.exceptions     import ValidationError
from django.db                  import models as m
from django.db.models           import Q
from jsonfield                  import JSONField

from polychartQuery.csv               import Connection as CsvDsConn
from polychartQuery.googleAnalytics   import Connection as GoogleAnalyticsDsConn
from polychartQuery.sql               import MySqlConn, InfobrightConn, PostgreSqlConn
from polychart.main.utils             import secureStorage
from polychart.main.utils.tools       import randomCode

class JSUserInfo(m.Model):
  name = m.CharField(max_length=128)
  email = m.CharField(max_length=75, default='')
  company = m.CharField(max_length=128, default='')
  website = m.CharField(max_length=128, default='')
  stripe_customer_id = m.CharField(
      max_length=20,
      default='',
      unique=True,
      help_text='Stripe customer ID associated with this.')
  created = m.DateField(auto_now_add=True, help_text="")

class UserInfo(m.Model):
  user = m.OneToOneField(User, primary_key=True)
  company = m.CharField(max_length=128, default='', blank=True)
  title = m.CharField(max_length=128, default='')
  website = m.CharField(max_length=128, default='', blank=True)
  phone = m.CharField(max_length=32, default='', blank=True)
  stripe_customer_id = m.CharField(
      max_length=20,
      blank=True,
      default='',
      help_text='Stripe customer ID associated with this.')

  technical = m.NullBooleanField()

  interest = m.TextField(default='', blank=True)

  usecase = m.CharField(max_length=16, default='web', choices=(
    ('web',"Web-personal"),
    ('biz',"Web-business"),
    ('oem',"OEM"),
  ))

  def makeSalt():
    return secureStorage.generateSalt()

  secure_storage_salt = m.CharField(max_length=16, default=makeSalt)

  global_unique_id = m.CharField(max_length=64, default=randomCode, unique=True)

  @classmethod
  def get_user_info(cls, user):
    return cls.objects.get_or_create(user=user)[0]

  @property
  def is_internal(self):
    """
    Determines if the user is internal to Polychart.

    WARNING: Do not trust this property.
             We do not validate the email address of an account,
             so this property should not be used for authorization.
    """

    if self.user.is_staff or self.user.is_superuser:
      return True

    if self.user.email.endswith('polychart.com'):
      return True

    return False

  @property
  def full_name(self):
    first = self.user.first_name or ''
    last = self.user.last_name or ''
    return (first + ' ' + last).strip()

  @property
  def intercom_hash(self):
    return hmac.new(settings.INTERCOM_API_KEY, self.global_unique_id, hashlib.sha256).hexdigest()

  def __unicode__(self):
    return unicode(self.pk)

  class Meta:
    permissions = (
      ("view_graphbuilder","Can see the graphbuilder."),
    )

class ForgotPassword(m.Model):
  '''User requesting for 'forgot password'. token '''
  user = m.ForeignKey(User)
  code = m.CharField(unique=True, max_length=128, default=randomCode)
  created = m.DateTimeField(auto_now_add=True)
  expired = m.BooleanField(default=False)

  @property
  def link(self):
    return settings.HOST_URL + '/reset-password?' + \
      urllib.urlencode({'code':self.code})

  def expire_and_save(self):
    """
    Mark the current "forgot password" as expired.
    """
    self.expired = True
    self.save()

  def __unicode__(self):
    return self.code

DATA_SOURCE_FIELDS = [
  # field name, encryption key name, decrypted type
  ('user', None, None),
  ('name', None, None),
  ('type', None, None),
  ('connection_type', None, None),
  ('db_host', 'default', str),
  ('db_port', 'default', int),
  ('db_username', 'default', str),
  ('db_password', 'user', str),
  ('db_name', 'default', str),
  ('db_ssl_cert', 'default', str),
  ('db_unix_socket', 'default', str),
  ('ssh_username', 'default', str),
  ('ssh_host', 'default', str),
  ('ssh_port', 'default', int),
  ('ssh_key', 'user', str),
  ('oauth_refresh_token', None, str),
  ('ga_profile_id', None, int)
]

class DataSource(m.Model):
  """
  A source of data for a dashboard.
  """
  key = m.CharField(unique=True, max_length=128, default=randomCode) # used on client-side
  user = m.ForeignKey(User)
  name = m.CharField(max_length=256)
  type = m.CharField(
    max_length=16,
    choices=[
      ('mysql', 'MySQL database'),
      ('postgresql', 'PostgreSQL database'),
      ('infobright', 'Infobright database'),
      ('salesforce', 'Salesforce account'), # no longer an option!
      ('googleAnalytics', 'Google Analytics account'),
      ('csv', 'CSV file')
    ]
  )
  connection_type = m.CharField(
    max_length=16,
    default='direct',
    choices=[
      ('direct', 'Direct'),
      ('ssh', 'SSH')
    ]
  )
  db_host_cipher = m.CharField(max_length=512, null=True)
  db_port_cipher = m.CharField(max_length=32, null=True)
  db_username_cipher = m.CharField(max_length=512, null=True)
  db_password_cipher = m.CharField(max_length=512, null=True)
  db_name_cipher = m.CharField(max_length=512, null=True)
  db_ssl_cert_cipher = m.TextField(null=True)
  db_unix_socket_cipher = m.CharField(max_length=100, null=True)
  ssh_username_cipher = m.CharField(max_length=512, null=True)
  ssh_host_cipher = m.CharField(max_length=512, null=True)
  ssh_port_cipher = m.CharField(max_length=32, null=True)
  ssh_key_cipher = m.TextField(null=True)
  oauth_refresh_token = m.TextField(null=True)
  ga_profile_id = m.CharField(max_length=32, null=True)

  @staticmethod
  def create(secureStorageKey, dsArgs):
    result = {}

    for (name, value) in dsArgs.items():
      fieldInfo = None
      for f in DATA_SOURCE_FIELDS:
        if f[0] == name:
          fieldInfo = f

      if not fieldInfo:
        raise ValueError('Unknown data source field "%s"' % name)

      if not value:
        continue

      if fieldInfo[1]: # if encryption needed
        if fieldInfo[1] == 'default':
          key = secureStorage.DEFAULT_KEY
        elif fieldInfo[1] == 'user':
          key = secureStorageKey
        else:
          raise ValueError('Unknown key %s' % fieldInfo[1])

        result[name+'_cipher'] = secureStorage.encrypt(key, str(value))
      else:
        result[name] = value

    return DataSource(**result)

  def openConnection(self, request, secureStorageKey):
    keys = {
      'default': secureStorage.DEFAULT_KEY,
      'user': secureStorageKey
    }

    dsArgs = {}
    for (fieldName, keyName, typeFn) in DATA_SOURCE_FIELDS:
      if keyName:
        cipher = getattr(self, fieldName+'_cipher')
        key = keys[keyName]

        if not cipher:
          dsArgs[fieldName] = cipher
          continue

        dsArgs[fieldName] = typeFn(secureStorage.decrypt(key, cipher))
      else:
        dsArgs[fieldName] = getattr(self, fieldName)

    if self.type not in settings.ENABLED_DATA_SOURCE_TYPES:
      raise Exception('Data source type %s is disabled' % repr(self.type))

    if self.type == 'mysql':
      return MySqlConn(**dsArgs)
    elif self.type == 'infobright':
      return InfobrightConn(**dsArgs)
    elif self.type == 'postgresql':
      return PostgreSqlConn(**dsArgs)
    elif self.type == 'googleAnalytics':
      return GoogleAnalyticsDsConn(**dsArgs)
    elif self.type == 'csv':
      return CsvDsConn(**dsArgs)
    else:
      raise Exception('Unknown data source type: %s' % self.type)

class PendingDataSource(m.Model):
  """
  A temporary object created when a user completes the connection setup script
  or begins filling out the data source form
  """
  key = m.CharField(unique=True, max_length=128, default=randomCode) # used on client-side
  params_json = JSONField()
  created = m.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)
  user = m.ForeignKey(User, null=True)

class LocalDataSource(m.Model):
  """
  A data source from a file that a user has uploaded
  """
  datasource = m.ForeignKey(DataSource, unique=True, null=True)
  pendingdatasource = m.ForeignKey(PendingDataSource, unique=True, null=True)
  json = JSONField(null=True)

class Dashboard(m.Model):
  """
  A dashboard that a user has created using the Dashboard Builder (dbb).
  """
  key = m.CharField(unique=True, max_length=128, default=randomCode) # used on client-side
  user = m.ForeignKey(User)
  name = m.CharField(max_length=256)
  spec_json = m.TextField()
  created = m.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)
  modified = m.DateTimeField(auto_now=True, default=django.utils.timezone.now)

class DashboardDataTable(m.Model):
  """
  A reference from a dashboard to a table from a data source.
  """
  dashboard = m.ForeignKey(Dashboard)
  data_source = m.ForeignKey(DataSource)
  table_name = m.CharField(max_length=64)

class TutorialCompletion(m.Model):
  """
  A completion of a tutorial by a user.  Used to prevent reshowing a tutorials.
  """
  user = m.ForeignKey(User)
  date_completed = m.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)
  type = m.CharField(
    max_length=16,
    choices=[
      ('nux', 'New user experience'),
      ('ga', 'Google Analytics')
    ]
  )

"""
Querying methods
"""
def username_or_email(key):
  """
  return the user with the given email or username.

  username takes precedence over the email.
  """
  queryset = User.objects.filter(Q(username=key) | Q(email=key))
  querysetlen = len(queryset)
  if querysetlen == 0:
    return None
  if querysetlen == 1:
    return queryset[0]
  else:
    first = queryset[0]
    second = queryset[1]
    if first.username == key:
      return first
    else:
      return second

  return None

