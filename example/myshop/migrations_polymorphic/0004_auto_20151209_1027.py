# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myshop', '0003_add_polymorphic'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Order', 'verbose_name_plural': 'Orders'},
        ),
        migrations.AlterField(
            model_name='product',
            name='cms_pages',
            field=models.ManyToManyField(help_text='Choose list view this product shall appear on.', to='cms.Page', through='myshop.ProductPage'),
        ),
        migrations.AlterField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(to='filer.Image', through='myshop.ProductImage'),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Slug'),
        ),
    ]
