# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import email_auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('email_auth', '0002_auto_20151011_1652'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', email_auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
    ]
