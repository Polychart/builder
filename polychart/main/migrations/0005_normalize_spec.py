# -*- coding: utf-8 -*-
"""
Data migration that is needed for new dashboard specifications.
"""
from south.db import db
from south.v2 import DataMigration
from django.db import models

import datetime
import json
import logging
import pprint
import re
logger = logging.getLogger(__name__)

def normalizeName(name, tableName):
  if tableName is None or name == 'count(*)' or re.match('ga-(dimension|metric)(.*)', tableName):
    return name
  pattern = re.compile(r'(bin|count|unique|sum|mean)?[\(]?('+tableName+')?\.?([^,\)]*)(,[^\)]*)?[\)]?')
  match   = pattern.match(name)
  if match is None:
    return "{0}.{1}".format(tableName, name)
  elif match.group(1) is not None and match.group(4) is not None: # bin
    return "{0}({1}.{2},{3})".format(match.group(1), tableName, match.group(3), match.group(4)[1:])
  elif match.group(1) is not None:
    return "{0}({1}.{2})".format(match.group(1), tableName, match.group(3))
  else:
    return "{0}.{1}".format(tableName, match.group(3))

def processChartSpec(spec):
  tmp = []
  for layer in spec.get('layers', []):
    maybeTableName = spec.get('tableName', spec.get('meta', {}).get('tableName', None))
    if maybeTableName is None:
      maybeMeta = layer.get('meta', {}).values()
      for meta in maybeMeta:
        if 'tableName' in meta:
          maybeTableName = meta['tableName']
          break
    tmpLayer = {'meta': {}}
    for key, val in layer.iteritems():
      if 'var' in val:
        val['var'] = normalizeName(val['var'], val.get('tableName', maybeTableName))
        tmpLayer[key] = val
      elif key == 'meta':
        for mkey, mval in layer.get('meta', {}).iteritems():
          mkey = normalizeName(mkey, mval.get('tableName', maybeTableName))
          tmpLayer['meta'][mkey] = mval
      elif key == 'facet':
        var = val.get('var', None)
        if var is not None and type(var) is str:
          val['var'] = normalizeName(var, val.get('tableName', maybeTableName))
        elif type(var) is dict:
          val['var']['var'] = normalizeName(val['var'].get('var', ""), val.get('tableName', maybeTableName))
        tmpLayer['facet'] = val
      elif key == 'filter':
        tmpLayer['filter'] = {}
        for fkey, fval in val.iteritems():
          fkey = normalizeName(fkey, fval.get('tableName', maybeTableName))
          tmpLayer['filter'][fkey] = fval
      else:
        tmpLayer[key] = val
    tmp.append(tmpLayer)
  spec['layers'] = tmp
  return spec

def processNumeralSpec(spec):
  tmp = {}
  for key, val in spec['meta'].iteritems():
    key = normalizeName(key, spec['tableName'])
    tmp[key] = val
  spec['meta'] = tmp
  tmp = {}
  for fkey, fval in spec.get('filter', {}).iteritems():
    fkey = normalizeName(fkey, spec['tableName'])
    tmp[fkey] = fval
  spec['filter'] = tmp
  spec['value']['var'] = normalizeName(spec['value']['var'], spec['tableName'])
  return spec

def processTableSpec(spec):
  tmp = []
  for row in spec.get('rows', []):
    row['var'] = normalizeName(row['var'], spec['tableName'])
    tmp.append(row)
  spec['rows'] = tmp

  tmp = {}
  for key, val in spec['meta'].iteritems():
    key = normalizeName(key, spec['tableName'])
    tmp[key] = val
  spec['meta'] = tmp

  tmp = []
  for col in spec['values']:
    col['var'] = normalizeName(col['var'], spec['tableName'])
    tmp.append(col)
  spec['values'] = tmp
  return spec

class Migration(DataMigration):

  def forwards(self, orm):
    "Write your forwards methods here."
    # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
    for dash in orm.Dashboard.objects.all():
      dashspec = json.loads(dash.spec_json)
      for item in dashspec:
        if   item['itemType'] == 'ChartItem':
          spec = processChartSpec(item['spec'])
        elif item['itemType'] == 'NumeralItem':
          spec = processNumeralSpec(item['spec'])
        elif item['itemType'] == 'PivotTableItem':
          spec = processTableSpec(item['spec'])
        else:
          continue
        item['spec'] = spec
      dash.spec_json = json.dumps(dashspec)
      if not db.dry_run:
        dash.save()
      else:
        logger.info(pprint.PrettyPrinter().pformat(dashspec))

  def backwards(self, orm):
    "Write your backwards methods here."
    raise RuntimeError("Cannot reverse this migration")

  models = {
    u'auth.group': {
      'Meta': {'object_name': 'Group'},
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
      'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
    },
    u'auth.permission': {
      'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
      'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
      'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
    },
    u'auth.user': {
      'Meta': {'object_name': 'User'},
      'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
      'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
      'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
      'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
      'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
      'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
      'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
      'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
      'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
      'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
      'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
    },
    u'contenttypes.contenttype': {
      'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
      'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
      'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
    },
    u'main.dashboard': {
      'Meta': {'object_name': 'Dashboard'},
      'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'key': ('django.db.models.fields.CharField', [], {'default': "'suRtfu-6xAjWhKGS-7S8PiN7'", 'unique': 'True', 'max_length': '128'}),
      'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
      'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
      'spec_json': ('django.db.models.fields.TextField', [], {}),
      'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
    },
    u'main.dashboarddatatable': {
      'Meta': {'object_name': 'DashboardDataTable'},
      'dashboard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Dashboard']"}),
      'data_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.DataSource']"}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'table_name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
    },
    u'main.datasource': {
      'Meta': {'object_name': 'DataSource'},
      'connection_type': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '16'}),
      'db_host_cipher': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
      'db_name_cipher': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
      'db_password_cipher': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
      'db_port_cipher': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
      'db_ssl_cert_cipher': ('django.db.models.fields.TextField', [], {'null': 'True'}),
      'db_unix_socket_cipher': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
      'db_username_cipher': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
      'ga_profile_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'key': ('django.db.models.fields.CharField', [], {'default': "'84TMMV3H9qU7d8Au6X-Fjpf3'", 'unique': 'True', 'max_length': '128'}),
      'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
      'oauth_refresh_token': ('django.db.models.fields.TextField', [], {'null': 'True'}),
      'ssh_host_cipher': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
      'ssh_key_cipher': ('django.db.models.fields.TextField', [], {'null': 'True'}),
      'ssh_port_cipher': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
      'ssh_username_cipher': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
      'type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
      'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
    },
    u'main.forgotpassword': {
      'Meta': {'object_name': 'ForgotPassword'},
      'code': ('django.db.models.fields.CharField', [], {'default': "'H1BC2AkwxKjEo95o81hEvzRh'", 'unique': 'True', 'max_length': '128'}),
      'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
      'expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
    },
    u'main.jsuserinfo': {
      'Meta': {'object_name': 'JSUserInfo'},
      'company': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
      'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
      'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '75'}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
      'stripe_customer_id': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '20'}),
      'website': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'})
    },
    u'main.localdatasource': {
      'Meta': {'object_name': 'LocalDataSource'},
      'datasource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.DataSource']", 'unique': 'True', 'null': 'True'}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'json': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
      'pendingdatasource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.PendingDataSource']", 'unique': 'True', 'null': 'True'})
    },
    u'main.pendingdatasource': {
      'Meta': {'object_name': 'PendingDataSource'},
      'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'key': ('django.db.models.fields.CharField', [], {'default': "'XX5bc9_gdNBdtrqmIiCoxKTY'", 'unique': 'True', 'max_length': '128'}),
      'params_json': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
      'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
    },
    u'main.tutorialcompletion': {
      'Meta': {'object_name': 'TutorialCompletion'},
      'date_completed': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
      u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
      'type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
      'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
    },
    u'main.userinfo': {
      'Meta': {'object_name': 'UserInfo'},
      'company': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
      'global_unique_id': ('django.db.models.fields.CharField', [], {'default': "'RTNDq6YJ9tvKfG9AO2sqMquu'", 'unique': 'True', 'max_length': '64'}),
      'interest': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
      'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
      'secure_storage_salt': ('django.db.models.fields.CharField', [], {'default': "'fvCSPiQDCmw='", 'max_length': '16'}),
      'stripe_customer_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
      'technical': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
      'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
      'usecase': ('django.db.models.fields.CharField', [], {'default': "'web'", 'max_length': '16'}),
      'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
      'website': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
    }
  }

  complete_apps = ['main']
  symmetrical = True
