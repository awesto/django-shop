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
                ('user', models.ForeignKey(orm[u'shop.user'], null=False)),
                ('group', models.ForeignKey(orm[u'auth.group'], null=False))
            ))
            db.create_unique(m2m_table_name, ['user_id', 'group_id'])
    
            # Adding M2M table for field user_permissions on 'User'
            m2m_table_name = db.shorten_name(u'auth_user_user_permissions')
            db.create_table(m2m_table_name, (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('user', models.ForeignKey(orm[u'shop.user'], null=False)),
                ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
            ))
            db.create_unique(m2m_table_name, ['user_id', 'permission_id'])
        except OperationalError:
            print "Reuse existing tables `auth_user`, `auth_user_groups` and `auth_user_user_permissions`."
            db.alter_column(u'auth_user', 'email', self.gf('django.db.models.fields.CharField')(max_length=254, unique=True, default=None, null=True))


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
        u'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'all_files'", 'null': 'True', 'to': u"orm['filer.Folder']"}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'owned_files'", 'null': 'True', 'to': u"orm['shop.User']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_filer.file_set+'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'sha1': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '40', 'blank': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'filer.folder': {
            'Meta': {'ordering': "(u'name',)", 'unique_together': "((u'parent', u'name'),)", 'object_name': 'Folder'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'filer_owned_folders'", 'null': 'True', 'to': u"orm['shop.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['filer.Folder']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'post_office.emailtemplate': {
            'Meta': {'unique_together': "((u'language', u'default_template'),)", 'object_name': 'EmailTemplate'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_template': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'translated_templates'", 'null': 'True', 'to': u"orm['post_office.EmailTemplate']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'html_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '12', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'shop.notification': {
            'Meta': {'object_name': 'Notification'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['post_office.EmailTemplate']"}),
            'mail_to': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'transition_target': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'shop.notificationattachment': {
            'Meta': {'object_name': 'NotificationAttachment'},
            'attachment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'email_attachment'", 'null': 'True', 'to': u"orm['filer.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shop.Notification']"})
        },
        u'shop.user': {
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['shop']