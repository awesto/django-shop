.. _multilingual-product:

===============================
Modeling a Multilingual Product
===============================

Let's extend our previous ``SmartCard`` model to internationalize our shop site. Normally the name
of a Smart Card model is international anyway, say *Ultra Plus micro SDXC*, so it probably won't
make much sense to use a translatable field here. The only model field which makes sense to be
available in different languages, is the ``description`` field.


Run the Multilingual Demo
=========================

To test this example, set the shell environment variable ``export DJANGO_SHOP_TUTORIAL=i18n``,
then recreate the database as explained in :ref:`create-demo-database`.

Afterwards start the demo server:

.. code-block:: shell

	./manage.py runserver


The Multilingal Product Model
=============================

**DjangoSHOP** uses the application django-parler_ for model translations. We therefore shall
rewrite our model as:

.. _django-parler: https://github.com/edoburu/django-parler

.. literalinclude:: /../example/myshop/models/i18n/smartcard.py
	:caption: myshop/models/i18n/smartcard.py
	:linenos:
	:language: python
	:lines: 8-10, 12, 15-18, 21-22, 27-28, 49, 77-
	:emphasize-lines: 11, 18-19

In comparison to the simple Smart Card model, the field ``description`` can now accept text in
different languages.

In order to work properly, a model with translations requires an additional model manager and a
table storing the translated fields. Accessing an instance of this model behaves exactly the same
as an untranslated model. Therefore it can be used as a drop-in replacement for our simple
``SmartCard`` model.


Translatable model in Django Admin
==================================

The admin requires only a small change. Its class must additionally inherit from
``TranslatableAdmin``. This adds a tab for each configured language to the top of the detail
editor. Therefore it is recommended to group all multilingual fields into one fieldset to emphasize
that these fields are translatable.

.. literalinclude:: /../example/myshop/admin/i18n/smartcard.py
	:caption: myshop/admin/i18n/smartcard.py
	:linenos:
	:language: python
	:lines: 3-9, 12-
