# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models, migrations
import filer.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        ('post_office', '0002_add_i18n_and_backend_alias'),
    ]
    if 'email_auth' in settings.INSTALLED_APPS:
        dependencies.append(('email_auth', '0001_initial'))
        customer_bases = ('email_auth.user',)
    else:
        dependencies.append(('auth', '0001_initial'))
        customer_bases = ('auth.user',)

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('transition_target', models.CharField(max_length=50, verbose_name='Event')),
                ('mail_to', models.PositiveIntegerField(default=None, null=True, verbose_name='Mail to', blank=True)),
                ('mail_template', models.ForeignKey(verbose_name='Template', to='post_office.EmailTemplate')),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NotificationAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment', filer.fields.file.FilerFileField(related_name='email_attachment', blank=True, to='filer.File', null=True)),
                ('notification', models.ForeignKey(to='shop.Notification')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomerProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Customer',
                'proxy': True,
                'verbose_name_plural': 'Customers',
            },
            bases=customer_bases,
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('post_office.email',),
        ),
    ]
