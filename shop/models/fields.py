# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection

POSTGRES_FALG = False
if str(connection.vendor) == 'postgresql':
    POSTGRES_FALG = True

try:
    if POSTGRES_FALG:
        from django.contrib.postgres.fields import JSONField
    else:
        raise ImportError
except ImportError:
    from jsonfield.fields import JSONField


class JSONFieldWrapper(JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'default': {}})
        super(JSONFieldWrapper, self).__init__(*args, **kwargs)
