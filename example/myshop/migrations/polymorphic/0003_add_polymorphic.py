# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import cms.models.fields
import djangocms_text_ckeditor.fields
import shop.money.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('filer', '0002_auto_20150606_2003'),
        ('myshop', '0002_add_i18n'),
    ]

    operations = [
        migrations.CreateModel(
            name='OperatingSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('active', models.BooleanField(default=True, help_text='Is this product publicly visible.', verbose_name='Active')),
                ('product_name', models.CharField(max_length=255, verbose_name='Product Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('order', models.PositiveIntegerField(verbose_name='Sort by', db_index=True)),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='ProductTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('description', djangocms_text_ckeditor.fields.HTMLField(help_text='Description for the list view of products.', verbose_name='Description')),
            ],
        ),
        migrations.CreateModel(
            name='SmartPhone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product_code', models.CharField(unique=True, max_length=255, verbose_name='Product code')),
                ('unit_price', shop.money.fields.MoneyField(default='0', help_text='Net price for this product', max_digits=30, decimal_places=3, verbose_name='Unit price')),
                ('storage', models.PositiveIntegerField(help_text='Internal storage in MB', verbose_name='Internal Storage')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='smartcardtranslation',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='smartcardtranslation',
            name='master',
        ),
        migrations.AlterModelOptions(
            name='smartcard',
            options={'verbose_name': 'Smart Card', 'verbose_name_plural': 'Smart Cards'},
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='active',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='cms_pages',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='id',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='images',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='manufacturer',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='order',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='product_name',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='smartcard',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(to='myshop.Product'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Product', blank=True, to='myshop.Product', null=True),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(to='myshop.Product'),
        ),
        migrations.AlterField(
            model_name='productpage',
            name='product',
            field=models.ForeignKey(to='myshop.Product'),
        ),
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('product_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myshop.Product')),
                ('unit_price', shop.money.fields.MoneyField(default='0', help_text='Net price for this product', max_digits=30, decimal_places=3, verbose_name='Unit price')),
                ('product_code', models.CharField(unique=True, max_length=255, verbose_name='Product code')),
                ('placeholder', cms.models.fields.PlaceholderField(slotname='Commodity Details', editable=False, to='cms.Placeholder', null=True)),
            ],
            options={
                'verbose_name': 'Commodity',
                'verbose_name_plural': 'Commodities',
            },
            bases=('myshop.product',),
        ),
        migrations.CreateModel(
            name='SmartPhoneModel',
            fields=[
                ('product_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myshop.Product')),
                ('battery_type', models.PositiveSmallIntegerField(verbose_name='Battery type', choices=[(1, 'Lithium Polymer (Li-Poly)'), (2, 'Lithium Ion (Li-Ion)')])),
                ('battery_capacity', models.PositiveIntegerField(help_text='Battery capacity in mAh', verbose_name='Capacity')),
                ('ram_storage', models.PositiveIntegerField(help_text='RAM storage in MB', verbose_name='RAM')),
                ('wifi_connectivity', models.PositiveIntegerField(help_text='WiFi Connectivity', verbose_name='WiFi', choices=[(1, '802.11 b/g/n')])),
                ('bluetooth', models.PositiveIntegerField(help_text='Bluetooth Connectivity', verbose_name='Bluetooth', choices=[(1, 'Bluetooth 4.0')])),
                ('gps', models.BooleanField(default=False, help_text='GPS integrated', verbose_name='GPS')),
                ('width', models.DecimalField(help_text='Width in mm', verbose_name='Width', max_digits=4, decimal_places=1)),
                ('height', models.DecimalField(help_text='Height in mm', verbose_name='Height', max_digits=4, decimal_places=1)),
                ('weight', models.DecimalField(help_text='Weight in gram', verbose_name='Weight', max_digits=5, decimal_places=1)),
                ('screen_size', models.DecimalField(help_text='Diagonal screen size in inch', verbose_name='Screen size', max_digits=4, decimal_places=2)),
                ('operating_system', models.ForeignKey(verbose_name='Operating System', to='myshop.OperatingSystem')),
            ],
            options={
                'verbose_name': 'Smart Phone',
                'verbose_name_plural': 'Smart Phones',
            },
            bases=('myshop.product',),
        ),
        migrations.DeleteModel(
            name='SmartCardTranslation',
        ),
        migrations.AddField(
            model_name='producttranslation',
            name='master',
            field=models.ForeignKey(related_name='translations', to='myshop.Product', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='cms_pages',
            field=models.ManyToManyField(help_text='Choose list view this product shall appear on.', to='cms.Page', through='myshop.ProductPage'),
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(to='filer.Image', through='myshop.ProductImage'),
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer',
            field=models.ForeignKey(verbose_name='Manufacturer', to='myshop.Manufacturer'),
        ),
        migrations.AddField(
            model_name='product',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_myshop.product_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='smartcard',
            name='product_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=None, serialize=False, to='myshop.Product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='smartphone',
            name='product',
            field=models.ForeignKey(verbose_name='Smart-Phone Model', to='myshop.SmartPhoneModel'),
        ),
        migrations.AlterUniqueTogether(
            name='producttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
