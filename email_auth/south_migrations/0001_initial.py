# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db.utils import OperationalError


class Migration(SchemaMigration):

    def forwards(self, orm):
        try:
            # This block only passes for fresh installs, otherwise syncdb has added these tables already.
            # Adding model 'User'
            db.create_table(u'auth_user', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
                ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
                ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('email', self.gf('django.db.models.fields.EmailField')(default=None, max_length=254, unique=True, null=True)),
                ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
                ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
                ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
                ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
                ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ))
            db.send_create_signal(u'shop', ['User'])
    
            # Adding M2M table for field groups on 'User'
            m2m_table_name = db.shorten_name(u'auth_user_groups')
            db.create_table(m2m_table_name, (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('user', models.ForeignKey(orm[u'email_auth.user'], null=False)),
                ('group', models.ForeignKey(orm[u'auth.group'], null=False))
            ))
            db.create_unique(m2m_table_name, ['user_id', 'group_id'])
    
            # Adding M2M table for field user_permissions on 'User'
            m2m_table_name = db.shorten_name(u'auth_user_user_permissions')
            db.create_table(m2m_table_name, (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('user', models.ForeignKey(orm[u'email_auth.user'], null=False)),
                ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
            ))
            db.create_unique(m2m_table_name, ['user_id', 'permission_id'])
        except OperationalError:
            print "Reuse existing tables `auth_user`, `auth_user_groups` and `auth_user_user_permissions`."
            db.alter_column(u'auth_user', 'email', self.gf('django.db.models.fields.CharField')(max_length=254, unique=True, default=None, null=True))
        finally:
            print "Check if column `auth_user.email` has a max_legth of 254 and is unique."

    def backwards(self, orm):
        print "Backward migration does not delete tables `auth_user`, `auth_user_groups` and `auth_user_user_permissions`."

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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'email_auth.user': {
            'Meta': {'object_name': 'User', 'db_table': "u'auth_user'"},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '254', 'unique': 'True', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
        }
    }

    complete_apps = ['email_auth']