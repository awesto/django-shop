# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.version import LooseVersion
import re
import subprocess
from django.db import connection

POSTGRES_FLAG = False
if str(connection.vendor) == 'postgresql':
    POSTGRES_FLAG = True
try:
    if POSTGRES_FLAG:
        import psycopg2

        psycopg2_version = re.search('([0-9.]+)', psycopg2.__version__ or "0").group(0)
        try:
            process = subprocess.Popen(
                ['psql', '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except (OSError, IOError):
            raise ImportError
        out, err = process.communicate()
        postgres_version = re.search('([0-9.]+)', out or "0").group(0)
        # To be able to use the Django version of JSONField, it requires to have PostgreSQL ≥ 9.4 and psycopg2 ≥ 2.5.4,
        # otherwise some issues could be faced.
        if LooseVersion(psycopg2_version) >= LooseVersion('2.5.4') and (LooseVersion(postgres_version)>= LooseVersion('9.4')):
            from django.contrib.postgres.fields import JSONField
        else:
            raise ImportError
    else:
        raise ImportError

except ImportError:
    from jsonfield.fields import JSONField


class JSONFieldWrapper(JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'default': {}})
        super(JSONFieldWrapper, self).__init__(*args, **kwargs)
