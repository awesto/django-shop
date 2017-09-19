========
Settings
========

These is the complete list of setting directives available for **django-SHOP**.

Usage in your own code:

.. code-block:: python

	from shop.conf import app_settings

	print(app_settings.APP_LABEL)

.. note:: When using as shown here, you don't have to prefix the settings property with ``SHOP_...``.

.. autoclass:: shop.conf.DefaultSettings
   :members:
