# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import djangocms_text_ckeditor.fields


def move_description(apps, schema_editor):
    SmartCard = apps.get_model('myshop', 'SmartCard')
    Translation = apps.get_model('myshop', 'SmartCardTranslation')
    for sc in SmartCard.objects.all():
        for lang in settings.LANGUAGES:
            trans = Translation.objects.create(language_code=lang[0], description=sc.description, master=sc)
            trans.save()


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
        migrations.AddField(
            model_name='smartcardtranslation',
            name='master',
            field=models.ForeignKey(related_name='translations', to='myshop.SmartCard', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='smartcardtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.RunPython(move_description),
        migrations.RemoveField(
            model_name='smartcard',
            name='description',
        ),
    ]
