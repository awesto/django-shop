# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('myshop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmartCardTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('description', djangocms_text_ckeditor.fields.HTMLField(help_text='Description for the list view of products.', verbose_name='Description')),
            ],
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='description',
        ),
        migrations.AddField(
            model_name='smartcardtranslation',
            name='master',
            field=models.ForeignKey(related_name='translations', to='myshop.SmartCard', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='smartcardtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
