# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ('transition_target', 'mail_to'), 'verbose_name': 'Notification', 'verbose_name_plural': 'Notifications'},
        ),
    ]
