# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.execute(u'DROP TABLE IF EXISTS analytics_event')
        db.rename_table(u'main_event', u'analytics_event')


    def backwards(self, orm):
        # Adding model 'Event'
        db.create_table(u'main_event', (
            ('session', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=256, null=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('cid', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'main', ['Event'])


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
            'key': ('django.db.models.fields.CharField', [], {'default': "'oV_yQe6j8qmhAmZ8QgkLjDvG'", 'unique': 'True', 'max_length': '128'}),
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
            'key': ('django.db.models.fields.CharField', [], {'default': "'7XdYiYAq9Om9snTbUMRJwtq4'", 'unique': 'True', 'max_length': '128'}),
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
            'code': ('django.db.models.fields.CharField', [], {'default': "'qaWFk-XsuT05OItm_0qaxMbN'", 'unique': 'True', 'max_length': '128'}),
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
            'key': ('django.db.models.fields.CharField', [], {'default': "'G3HEb5xGNGDMePHCxKYyyLPR'", 'unique': 'True', 'max_length': '128'}),
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
            'global_unique_id': ('django.db.models.fields.CharField', [], {'default': "'f2AiaA1XfyR2CsAlBT4R5Eks'", 'unique': 'True', 'max_length': '64'}),
            'interest': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'secure_storage_salt': ('django.db.models.fields.CharField', [], {'default': "'2fPbpXemn_k='", 'max_length': '16'}),
            'stripe_customer_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'technical': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'usecase': ('django.db.models.fields.CharField', [], {'default': "'web'", 'max_length': '16'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
        }
    }

    complete_apps = ['main']
