# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myshop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='smartcard',
            name='speed',
            field=models.CharField(default=4, max_length=8, verbose_name='Transfer Speed', choices=[(4, '4 MB/s'), (20, '20 MB/s'), (30, '30 MB/s'), (40, '40 MB/s'), (48, '48 MB/s'), (80, '80 MB/s'), (95, '95 MB/s'), (280, '280 MB/s')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='smartcard',
            name='card_type',
            field=models.CharField(max_length=15, verbose_name='Card Type', choices=[('SD', 'SD'), ('micro SD', 'micro SD'), ('SDXC', 'SDXC'), ('micro SDXC', 'micro SDXC'), ('SDHC', 'SDHC'), ('micro SDHC', 'micro SDHC')]),
            preserve_default=True,
        ),
    ]
