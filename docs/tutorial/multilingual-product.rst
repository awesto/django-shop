.. _tutorial/multilingual-product:

===============================
Modeling a Multilingual Product
===============================

Let's extend our previous ``SmartCard`` model to internationalize our shop site. Normally the name
of a Smart Card model is international anyway, say "*Ultra Plus micro SDXC*", so it probably won't
make much sense to use a translatable field here. The model attribute which certainly makes sense
to be translated into different languages, is the ``description`` field.


Run the Multilingual Demo
=========================

To test this example, set the shell environment variable ``export DJANGO_SHOP_TUTORIAL=i18n``,
then apply the modified models to the database schema:

.. code-block:: shell

	./manage.py migrate myshop

Alternatively recreate the database as explained in :ref:`tutorial/create-demo-database`.

Afterwards start the demo server:

.. code-block:: shell

	./manage.py runserver


The Multilingal Product Model
=============================

**DjangoSHOP** uses the library django-parler_ for model translations. We therefore shall
rewrite our model as:

.. _django-parler: https://github.com/edoburu/django-parler

.. literalinclude:: /../example/myshop/models/i18n/smartcard.py
	:caption: myshop/models/i18n/smartcard.py
	:linenos:
	:language: python
	:lines: 7-15, 17-19, 21-23, 26-31, 49-50, 80-
	:emphasize-lines: 21, 28-29

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
	:lines: 4-10, 12-
	:emphasize-lines: 15-17


Extend our discrete product type, to polymorphic models which are able to support many different
product types: :ref:`tutorial/polymorphic-product`.
