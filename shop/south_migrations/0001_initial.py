# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        print "Dummy migration to initialize django-shop. All migrations are performed from your app"

    def backwards(self, orm):
        pass

    models = {
        
    }

    complete_apps = ['shop']
