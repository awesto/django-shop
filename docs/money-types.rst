===========
Money types
===========

Until **django-shop** version 0.2, amounts relating to money, where kept inside a ``Decimal`` type
and stored in the database model with ``DecimalField``. On shop installations with only one
available currency, this wasn't a major issue, because the currency symbol could be hard-coded
anywhere on the site.

However, for sites offering pricing information in more than one currency, this could lead to
major problems. When you need to perform calculations with amounts that have an associated currency,
it is a very common to make mistakes by mixing different currencies. It is also common to perform
incorrect conversions that generate wrong results. Python doesn't allow developers to associate a
specific decimal value with a unit.

**django-shop**, starting in version 0.3.0 is shipped with with a special factory class


MoneyMaker
==========

This class can not be instantiated, but is a factory for building a money type with an associated
currency. Internally it uses the well established ``Decimal`` type to keep track of amount.
Additionally it restricts operations on the current Money type. For instance, you can't sum up
Dollars with Euros. You also can't multiply two money types with each other.


Create a Money type
-------------------

.. code-block:: python

	>>> from shop.money_maker import MoneyMaker
	>>> Money = MoneyMaker()
	>>> print Money('1.99')
	€ 1.99
	
	>>> print Money('1.55') + Money('8')
	€ 9.55
	
	>>> print Money
	<class 'shop.money.money_maker.MoneyInEUR'>
	
	>>> Yen = MoneyMaker('JPY')
	>>> print Yen('1234.5678')
	¥ 1235
	
	>>> print Money('100') + Yen('1000')
	ValueError: Can not add/substract money in different currencies.

How does this work?

By calling ``MoneyMaker()`` a type accepting amounts in the *default currency* is created.
The default currency can be changed in ``settings.py`` with ``SHOP_DEFAULT_CURRENCY = 'USD'``,
using one of the official ISO-4217 currency codes.

Alternatively, you can create your own money type, for example ``Yen``.


Printing Money
--------------

When the amount of a money type is printed, or forced to text using ``str(price)``, it is prefixed
by the currency symbol. This is fine, if you work with only a few currencies. However, some symbols
are ambiguous.

With the setting ``SHOP_MONEY_FORMAT`` you can style how money is going to be printed. This
settings defaults to ``{symbol} {amount}``. The following format strings are allowed:

 * ``{symbol}``: The short symbol for a currency, for instance ``$``, ``£``, ``€``, ``¥``, etc.
 * ``{code}``: The international currency code, for instance USD, GBP, EUR, JPY, etc.
 * ``{currency}``: The spoken currency description, for instance “US Dollar”, “Pound Sterling”, etc.
 * ``{amount}``: The amount, unlocalized.

Thus, if you prefer to print ``9.98 US Dollar``, then use ``{amount} {currency}`` as formatting
string.


Localizing Money
================

Since the Money class doesn't know anything about your current locale setting, amounts always are
printed unlocalized. To localize a money type, use ``django.utils.numberformat.format(someamount)``.
This function will return the amount, localized according to your current HTTP request.


Money Database Fields
=====================

Money can be stored in the database, keeping the currency information together with the field type.
Internally, the database uses the Decimal type, but such a field knows its currency and will return
an amount as ``MoneyIn...`` type. This prevent from implicit, but accidental currency conversions.

In your database model, declare a field as:

.. code-block:: python

	class Product(models.Model):
	    ...
	    unit_price = MoneyField(currency='GBP')

This field stores its amounts as British Pounds and returns them typed as ``MoneyInGBP``.
If the ``currency`` argument is omitted, then the default currency is used.


Money Representation in JSON
============================

An additional REST SerializerField has been added to convert amounts into JSON strings. When
writing REST serializers, use:

.. code-block:: python

	from rest_framework import serializers
	from shop.money.rest import MoneyField
	
	class SomeSerializer(serializers.ModelSerializer):
	    price = MoneyField()

The default REST behavior, is to serialize Decimal types as floats. This is fine if you want to
do some calculations in the browser. However, than the currency information is lost, and must
be somehow readded to the output strings. It also is a bad idea to do commercial calculations using
floats, but JavaScript does not have any built-in Decimal type. I therefore recommend to always
do your commerce calculations on the server and pass amount information using JSON strings.
