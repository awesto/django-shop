# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection

from shop.apps import get_tuple_version

try:
    if str(connection.vendor) == 'postgresql':
        import psycopg2

        psycopg2_version = get_tuple_version(psycopg2.__version__[:5])
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            row = cursor.fetchone()[:17]
        postgres_version = get_tuple_version(str(row[0][:17].split(' ')[1]))
        # To be able to use the Django version of JSONField, it requires to have
        # PostgreSQL ≥ 9.4 and psycopg2 ≥ 2.5.4, otherwise some issues could be faced.
        if (psycopg2_version[0]) >= (2, 5, 4) and (postgres_version >= (9, 4)):
            from django.contrib.postgres.fields import JSONField as _JSONField
        else:
            raise ImportError
    else:
        raise ImportError

except ImportError:
    from jsonfield.fields import JSONField as _JSONField


class JSONField(_JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'default': {}})
        super(JSONField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(JSONField, self).deconstruct()
        del kwargs['default']
        return name, path, args, kwargs
