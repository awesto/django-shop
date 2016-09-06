# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.version import LooseVersion
import re
from django.db import connection

POSTGRES_FLAG = False
if str(connection.vendor) == 'postgresql':
    POSTGRES_FLAG = True
try:
    import psycopg2

    version = re.search('([0-9.]+)', psycopg2.__version__ or "0").group(0)
    if POSTGRES_FLAG and (LooseVersion(version) >= LooseVersion('2.5.4')):
        from django.contrib.postgres.fields import JSONField
    else:
        raise ImportError
except ImportError:
    from jsonfield.fields import JSONField


class JSONFieldWrapper(JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'default': {}})
        super(JSONFieldWrapper, self).__init__(*args, **kwargs)
