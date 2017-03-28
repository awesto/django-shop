.. _upgrading:

=====================
Upgrading django-SHOP
=====================

.. _upgrading-0.10:

Upgrading to 0.10.0
===================

This version requires **django-CMS** version 3.4.2 or higher and **djangocms-cascade** version
0.12.0 or higher. It is well tested with Django-1.10 but should work as well with Django-1.9.

There has been a lot of effort in getting a cleaner and more consistent API. If you upgrade from
version 0.9 please note the following changes:

The REST serializers have been moved into their own submodule ``shop.serializers``. They now are
separated into ``bases`` and ``defaults`` following the same naming convention as beeing used
in ``shop.models`` and ``shop.admin``. Please ensure that you change your import statements.

Serializers ``ProductCommonSerializer``, ``ProductSummarySerializer`` and ``ProductDetailSerializer``
have been unified into a single ``ProductSerializer``, which acts as default for the
``ProductListView`` and the ``ProductRetrieveView``. The ``ProductSummarySerializer`` (which is used
to serialize attributes available across all products of the site) now must be configured using the
settings directive ``SHOP_PRODUCT_SUMMARY_SERIALIZER``.

All Angular directives have been checked for HTML5 mode compatibility. It is strongly recommended
over hashbang mode.

Billing and shipping address have been unified into one single address form which makes them easier
to interchange. The ``salutation`` field has been removed from the address model and can now
optionally be added to the merchant representation.

All AngularJS directives for the catalog list and catalog search view support infinite scroll, as
well as manual pagination.

After upgrading to **angular-ui-bootstrap** version 0.14, all corresponding directives have to be
prefixed with ``uib-...``.

There is no more need for a special URL pattern to handle auto-completion search. Instead use the
wrapping view :class:`shop.search.views.CMSPageCatalogWrapper`.

The model ``CartItem`` has a new CharField ``product_code``. This replaces the ``product_code``
otherwise kept inside its ``extra`` dict. This requires a database migration on the merchant
implementation. Such a migration file must contain a datamigration, for instance:

.. code-block:: python

	from __future__ import unicode_literals

	from django.db import migrations, models

	def forwards(apps, schema_editor):
	    CartItem = apps.get_model('myshop', 'CartItem')
	    for item in CartItem.objects.all():
	        item.product_code = item.extra.get('product_code', '')
	        item.save()


	def backwards(apps, schema_editor):
	    CartItem = apps.get_model('myshop', 'CartItem')
	    for item in CartItem.objects.all():
	        item.extra['product_code'] = item.product_code
	        item.save()


	class Migration(migrations.Migration):

	    dependencies = [
	        ('myshop', '0001_initial'),
	    ]

	    operations = [
	        migrations.AddField(
	            model_name='cartitem',
	            name='product_code',
	            field=models.CharField(blank=True, help_text='Product code of added item.', max_length=255, null=True, verbose_name='Product code'),
	        ),
	        migrations.RunPython(forwards, reverse_code=backwards),
	    ]



0.9.3
=====

This version requires **djangocms-cascade** 0.11.0 or higher. Please ensure to run the migrations
which convert the Cascade elements:

.. code-block:: bash

	./manage.py migrate shop


0.9.2
=====

The default address models have changed in 0.9.2. If you are upgrading from
0.9.0 or 0.9.1 and your project is using the default address models, you need
to add a migration to make the necessary changes to your models:

.. code-block:: bash

	./manage.py makemigrations --empty yourapp

Next, edit the migration file to look like this:

.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals

    from django.db import models, migrations


    class Migration(migrations.Migration):

        dependencies = [
            # makemgirations will generate the dependencies for you.
        ]

        operations = [
            migrations.RenameField("ShippingAddress", "addressee", "name"),
            migrations.RenameField("ShippingAddress", "street", "address1"),
            migrations.RenameField("ShippingAddress", "supplement", "address2"),
            migrations.RenameField("ShippingAddress", "location", "city"),

            migrations.AlterField("ShippingAddress", "name", models.CharField(
                verbose_name="Full name", max_length=1024
            )),
            migrations.AlterField("ShippingAddress", "address1", models.CharField(
                verbose_name="Address line 1", max_length=1024
            )),
            migrations.AlterField("ShippingAddress", "address2", models.CharField(
                verbose_name="Address line 2", max_length=1024
            )),
            migrations.AlterField("ShippingAddress", "city", models.CharField(
                verbose_name="City", max_length=1024
            )),

            migrations.RenameField("BillingAddress", "addressee", "name"),
            migrations.RenameField("BillingAddress", "street", "address1"),
            migrations.RenameField("BillingAddress", "supplement", "address2"),
            migrations.RenameField("BillingAddress", "location", "city"),

            migrations.AlterField("BillingAddress", "name", models.CharField(
                verbose_name="Full name", max_length=1024
            )),
            migrations.AlterField("BillingAddress", "address1", models.CharField(
                verbose_name="Address line 1", max_length=1024
            )),
            migrations.AlterField("BillingAddress", "address2", models.CharField(
                verbose_name="Address line 2", max_length=1024
            )),
            migrations.AlterField("BillingAddress", "city", models.CharField(
                verbose_name="City", max_length=1024
            )),
        ]


Finally, apply the migration::

    ./manage.py migrate yourapp
