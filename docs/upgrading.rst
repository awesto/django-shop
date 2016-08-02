====================
Upgrade instructions
====================

0.9.2
=====
The default address models have changed in 0.9.2. If you are upgrading from
0.9.0 or 0.9.1 and your project is using the default address models, you need
to add a migration to make the necessary changes to your models::

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
