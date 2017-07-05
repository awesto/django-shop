# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

postgresql_engine_names = [
    'django.db.backends.postgresql',
    'django.db.backends.postgresql_psycopg2',
]

if settings.DATABASES['default']['ENGINE'] in postgresql_engine_names:
    from django.contrib.postgres.fields import JSONField as _JSONField
else:
    from jsonfield.fields import JSONField as _JSONField


class JSONField(_JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'default': {}})
        super(JSONField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(JSONField, self).deconstruct()
        del kwargs['default']
        return name, path, args, kwargs
