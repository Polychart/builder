# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'JSUserInfo'
        db.create_table(u'main_jsuserinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('email', self.gf('django.db.models.fields.CharField')(default='', max_length=75)),
            ('company', self.gf('django.db.models.fields.CharField')(default='', max_length=128)),
            ('website', self.gf('django.db.models.fields.CharField')(default='', max_length=128)),
            ('stripe_customer_id', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=20)),
            ('created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['JSUserInfo'])

        # Adding model 'UserInfo'
        db.create_table(u'main_userinfo', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('company', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=128)),
            ('website', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True)),
            ('stripe_customer_id', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('technical', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('interest', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('usecase', self.gf('django.db.models.fields.CharField')(default='web', max_length=16)),
            ('secure_storage_salt', self.gf('django.db.models.fields.CharField')(default='JQVtaWT6IN0=', max_length=16)),
        ))
        db.send_create_signal(u'main', ['UserInfo'])

        # Adding model 'ForgotPassword'
        db.create_table(u'main_forgotpassword', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('code', self.gf('django.db.models.fields.CharField')(default='Ozi-9xgYrUiAoiXL5ZH2Rr0r', unique=True, max_length=128)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expired', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'main', ['ForgotPassword'])

        # Adding model 'Event'
        db.create_table(u'main_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('session', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('cid', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
        ))
        db.send_create_signal(u'main', ['Event'])

        # Adding model 'DataSource'
        db.create_table(u'main_datasource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(default='_gTw0rWAjhSLgc0OWv3NXNBL', unique=True, max_length=128)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('connection_type', self.gf('django.db.models.fields.CharField')(default='direct', max_length=16)),
            ('db_host_cipher', self.gf('django.db.models.fields.CharField')(max_length=512, null=True)),
            ('db_port_cipher', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('db_username_cipher', self.gf('django.db.models.fields.CharField')(max_length=512, null=True)),
            ('db_password_cipher', self.gf('django.db.models.fields.CharField')(max_length=512, null=True)),
            ('db_name_cipher', self.gf('django.db.models.fields.CharField')(max_length=512, null=True)),
            ('db_ssl_cert_cipher', self.gf('django.db.models.fields.TextField')(null=True)),
            ('db_unix_socket_cipher', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('ssh_username_cipher', self.gf('django.db.models.fields.CharField')(max_length=512, null=True)),
            ('ssh_host_cipher', self.gf('django.db.models.fields.CharField')(max_length=512, null=True)),
            ('ssh_port_cipher', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('ssh_key_cipher', self.gf('django.db.models.fields.TextField')(null=True)),
            ('oauth_refresh_token', self.gf('django.db.models.fields.TextField')(null=True)),
            ('ga_profile_id', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
        ))
        db.send_create_signal(u'main', ['DataSource'])

        # Adding model 'PendingDataSource'
        db.create_table(u'main_pendingdatasource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(default='xXQCmPEGxX2GiCE0BJnulbP2', unique=True, max_length=128)),
            ('params_json', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['PendingDataSource'])

        # Adding model 'Dashboard'
        db.create_table(u'main_dashboard', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(default='O7WpfGtb7HduxPBoHu7KIPIE', unique=True, max_length=128)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('spec_json', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Dashboard'])

        # Adding model 'DashboardDataTable'
        db.create_table(u'main_dashboarddatatable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dashboard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Dashboard'])),
            ('data_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.DataSource'])),
            ('table_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'main', ['DashboardDataTable'])

        # Adding model 'TutorialCompletion'
        db.create_table(u'main_tutorialcompletion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date_completed', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal(u'main', ['TutorialCompletion'])


    def backwards(self, orm):
        # Deleting model 'JSUserInfo'
        db.delete_table(u'main_jsuserinfo')

        # Deleting model 'UserInfo'
        db.delete_table(u'main_userinfo')

        # Deleting model 'ForgotPassword'
        db.delete_table(u'main_forgotpassword')

        # Deleting model 'Event'
        db.delete_table(u'main_event')

        # Deleting model 'DataSource'
        db.delete_table(u'main_datasource')

        # Deleting model 'PendingDataSource'
        db.delete_table(u'main_pendingdatasource')

        # Deleting model 'Dashboard'
        db.delete_table(u'main_dashboard')

        # Deleting model 'DashboardDataTable'
        db.delete_table(u'main_dashboarddatatable')

        # Deleting model 'TutorialCompletion'
        db.delete_table(u'main_tutorialcompletion')


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
            'key': ('django.db.models.fields.CharField', [], {'default': "'EUOxWdp0tc3eS-vfS9mFZ1MC'", 'unique': 'True', 'max_length': '128'}),
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
            'key': ('django.db.models.fields.CharField', [], {'default': "'wnANI_BGeUN089uskbLZ2mBR'", 'unique': 'True', 'max_length': '128'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'oauth_refresh_token': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'ssh_host_cipher': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
            'ssh_key_cipher': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'ssh_port_cipher': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'ssh_username_cipher': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'main.event': {
            'Meta': {'object_name': 'Event'},
            'cid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'session': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'main.forgotpassword': {
            'Meta': {'object_name': 'ForgotPassword'},
            'code': ('django.db.models.fields.CharField', [], {'default': "'u7YszNL2-X6wpyqSlEy4qom7'", 'unique': 'True', 'max_length': '128'}),
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
        u'main.pendingdatasource': {
            'Meta': {'object_name': 'PendingDataSource'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'tA5KABuSyfLcuJ2ijiqIaRPr'", 'unique': 'True', 'max_length': '128'}),
            'params_json': ('django.db.models.fields.TextField', [], {})
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
            'interest': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'secure_storage_salt': ('django.db.models.fields.CharField', [], {'default': "'M9nGGrxbVkI='", 'max_length': '16'}),
            'stripe_customer_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'technical': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'usecase': ('django.db.models.fields.CharField', [], {'default': "'web'", 'max_length': '16'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
        }
    }

    complete_apps = ['main']