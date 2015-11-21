# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myshop', '0002_auto_20151120_1359'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='smartcard',
            options={'ordering': ('order',), 'verbose_name': 'Smart Card', 'verbose_name_plural': 'Smart Cards'},
        ),
    ]
