# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
from django.conf import settings
import jsonfield.fields
import shop.util.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Carts',
                'abstract': False,
                'verbose_name': 'Cart',
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('quantity', models.IntegerField()),
                ('cart', models.ForeignKey(related_name='items', to='shop.Cart')),
            ],
            options={
                'verbose_name_plural': 'Cart items',
                'abstract': False,
                'verbose_name': 'Cart item',
            },
        ),
        migrations.CreateModel(
            name='ExtraOrderItemPriceField',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('label', models.CharField(max_length=255, verbose_name='Label')),
                ('value', shop.util.fields.CurrencyField(max_digits=30, decimal_places=2, verbose_name='Amount', default=Decimal('0.0'))),
                ('data', jsonfield.fields.JSONField(blank=True, verbose_name='Serialized extra data', null=True)),
            ],
            options={
                'verbose_name_plural': 'Extra order item price fields',
                'verbose_name': 'Extra order item price field',
            },
        ),
        migrations.CreateModel(
            name='ExtraOrderPriceField',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('label', models.CharField(max_length=255, verbose_name='Label')),
                ('value', shop.util.fields.CurrencyField(max_digits=30, decimal_places=2, verbose_name='Amount', default=Decimal('0.0'))),
                ('data', jsonfield.fields.JSONField(blank=True, verbose_name='Serialized extra data', null=True)),
                ('is_shipping', models.BooleanField(editable=False, verbose_name='Is shipping', default=False)),
            ],
            options={
                'verbose_name_plural': 'Extra order price fields',
                'verbose_name': 'Extra order price field',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('status', models.IntegerField(choices=[(10, 'Processing'), (20, 'Confirming'), (30, 'Confirmed'), (40, 'Completed'), (50, 'Shipped'), (60, 'Canceled')], verbose_name='Status', default=10)),
                ('order_subtotal', shop.util.fields.CurrencyField(max_digits=30, decimal_places=2, verbose_name='Order subtotal', default=Decimal('0.0'))),
                ('order_total', shop.util.fields.CurrencyField(max_digits=30, decimal_places=2, verbose_name='Order Total', default=Decimal('0.0'))),
                ('shipping_address_text', models.TextField(blank=True, verbose_name='Shipping address', null=True)),
                ('billing_address_text', models.TextField(blank=True, verbose_name='Billing address', null=True)),
                ('created', models.DateTimeField(verbose_name='Created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='Updated', auto_now=True)),
                ('cart_pk', models.PositiveIntegerField(blank=True, verbose_name='Cart primary key', null=True)),
            ],
            options={
                'verbose_name_plural': 'Orders',
                'abstract': False,
                'verbose_name': 'Order',
            },
        ),
        migrations.CreateModel(
            name='OrderExtraInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('text', models.TextField(blank=True, verbose_name='Extra info')),
                ('order', models.ForeignKey(to='shop.Order', verbose_name='Order', related_name='extra_info')),
            ],
            options={
                'verbose_name_plural': 'Order extra info',
                'verbose_name': 'Order extra info',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('product_reference', models.CharField(max_length=255, verbose_name='Product reference')),
                ('product_name', models.CharField(max_length=255, blank=True, verbose_name='Product name', null=True)),
                ('unit_price', shop.util.fields.CurrencyField(max_digits=30, decimal_places=2, verbose_name='Unit price', default=Decimal('0.0'))),
                ('quantity', models.IntegerField(verbose_name='Quantity')),
                ('line_subtotal', shop.util.fields.CurrencyField(max_digits=30, decimal_places=2, verbose_name='Line subtotal', default=Decimal('0.0'))),
                ('line_total', shop.util.fields.CurrencyField(max_digits=30, decimal_places=2, verbose_name='Line total', default=Decimal('0.0'))),
                ('order', models.ForeignKey(to='shop.Order', verbose_name='Order', related_name='items')),
            ],
            options={
                'verbose_name_plural': 'Order items',
                'abstract': False,
                'verbose_name': 'Order item',
            },
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('amount', shop.util.fields.CurrencyField(max_digits=30, decimal_places=2, verbose_name='Amount', default=Decimal('0.0'))),
                ('transaction_id', models.CharField(max_length=255, verbose_name='Transaction ID', help_text="The transaction processor's reference")),
                ('payment_method', models.CharField(max_length=255, verbose_name='Payment method', help_text='The payment backend used to process the purchase')),
                ('order', models.ForeignKey(verbose_name='Order', to='shop.Order')),
            ],
            options={
                'verbose_name_plural': 'Order payments',
                'verbose_name': 'Order payment',
            },
        ),
        migrations.CreateModel(
            name='PaymentBackend',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('url_name', models.SlugField(max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('logo', models.ImageField(upload_to=shop.util.fields.upload_to_classname, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Payment backends',
                'abstract': False,
                'verbose_name': 'Payment backend',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(verbose_name='Slug', unique=True)),
                ('active', models.BooleanField(default=False, verbose_name='Active', db_index=True)),
                ('date_added', models.DateTimeField(verbose_name='Date added', auto_now_add=True)),
                ('last_modified', models.DateTimeField(verbose_name='Last modified', auto_now=True)),
                ('unit_price', shop.util.fields.CurrencyField(max_digits=30, decimal_places=2, verbose_name='Unit price', default=Decimal('0.0'))),
            ],
            options={
                'verbose_name_plural': 'Products',
                'abstract': False,
                'verbose_name': 'Product',
            },
        ),
        migrations.CreateModel(
            name='ShippingBackend',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('url_name', models.SlugField(max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('logo', models.ImageField(upload_to=shop.util.fields.upload_to_classname, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Shipping backends',
                'abstract': False,
                'verbose_name': 'Shipping backend',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, related_name='polymorphic_shop.product_set+'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(to='shop.Product', blank=True, verbose_name='Product', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_backend',
            field=models.ForeignKey(to='shop.PaymentBackend', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_backend',
            field=models.ForeignKey(to='shop.ShippingBackend', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, verbose_name='User', null=True),
        ),
        migrations.AddField(
            model_name='extraorderpricefield',
            name='order',
            field=models.ForeignKey(verbose_name='Order', to='shop.Order'),
        ),
        migrations.AddField(
            model_name='extraorderitempricefield',
            name='order_item',
            field=models.ForeignKey(verbose_name='Order item', to='shop.OrderItem'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(to='shop.Product'),
        ),
    ]
