# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cmsplugin_cascade.link.plugin_base
import shop.cascade.plugin_base


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0007_headingpluginmodel_horizontalrulepluginmodel_segmentpluginmodel_simplewrapperpluginmodel'),
        ('shop', '0002_auto_20151016_1451'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcceptConditionFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BillingAddressFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BreadcrumbPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='CatalogLinkPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='CheckoutAddressPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='CustomerFormPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='CustomerFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='DialogFormPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ExtraAnnotationFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='GuestFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='PaymentMethodFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ProcessBarPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ProcessNextStepPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(cmsplugin_cascade.link.plugin_base.LinkElementMixin, 'cmsplugin_cascade.cascadeelement'),
        ),
        migrations.CreateModel(
            name='ProcessStepPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='RequiredFormFieldsPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShippingAddressFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShippingMethodFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopAddToCartPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopAuthenticationPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(shop.cascade.plugin_base.ShopLinkElementMixin, 'cmsplugin_cascade.cascadeelement'),
        ),
        migrations.CreateModel(
            name='ShopButtonPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopCartPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopCatalogPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopLinkPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopOrderViewsPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopProceedButtonModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(cmsplugin_cascade.link.plugin_base.LinkElementMixin, 'cmsplugin_cascade.cascadeelement'),
        ),
        migrations.CreateModel(
            name='ShopSearchResultsPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
    ]
