.. _reference/money-types:

===========
Money Types
===========

In earlier versions of **django-SHOP**, amounts relating to money were kept inside a ``Decimal``
type and stored in the database model using a ``DecimalField``. In shop installations with only one
available currency, this wasn't a major issue, because the currency symbol could be hard-coded
anywhere on the site.

However, for sites offering pricing information in more than one currency, this caused major
problems. When we needed to perform calculations with amounts that have an associated currency,
it is very common to make mistakes by mixing different currencies. It also is common to perform
incorrect conversions that generate wrong results. Python doesn't allow developers to associate a
specific decimal value with a unit.

Starting with version 0.9, **django-SHOP** ships with a special factory class:


MoneyMaker
==========

This class can not be instantiated, but is a factory for building a money type with an associated
currency. Internally it uses the well established ``Decimal`` type to keep track of the amount.
Additionally, it restricts operations on the current Money type. For instance, we can't sum up
Dollars with Euros. We also can't multiply two currencies with each other.


Not a Number
------------

In special occurrences we'd rather want to specify "no amount" rather than an amount of 0.00 (zero).
This can be useful for free samples, or when an item currently is not available. The Decimal type
denotes a kind of special value a ``NaN`` – for "Not a Number". Our Money type therefore inherits
this special value, but renders it for instance as ``€ –`` or ``$ –``.

Declaring a Money object without a value, say ``m = Money()`` creates such a special value. The big
difference as for the ``Decimal`` type is that when adding or subtracting a ``NaN`` to a valid
value, it is considered zero, rather than changing the result of this operation to ``NaN`` as well.

It also allows us to multiply a Money amount with ``None``. The result of this operation is ``NaN``.


Create a Money type
-------------------

.. code-block:: python

	>>> from shop.money import MoneyMaker
	>>> Money = MoneyMaker()
	>>> print(Money('1.99'))
	€ 1.99

	>>> print(Money('1.55') + Money('8'))
	€ 9.55

	>>> print(Money)
	<class 'shop.money.money_maker.MoneyInEUR'>

	>>> Yen = MoneyMaker('JPY')
	>>> print(Yen('1234.5678'))
	¥ 1,235

	>>> print(Money('100') + Yen('1000'))
	ValueError: Can not add/substract money in different currencies.

How does this work?

By calling ``MoneyMaker()`` a type accepting amounts in the *default currency* is created.
The default currency can be changed in ``settings.py`` with ``SHOP_DEFAULT_CURRENCY = 'USD'``,
using one of the official ISO-4217 currency codes.

Alternatively, we can create our own Money type, for instance ``Yen``.


Formatting Money
----------------

When the amount of a money type is printed or forced to text using ``str(price)``, it is prefixed
by the currency symbol. This is fine, when working with only a few currencies. However, some symbols
are ambiguous, for instance Canadian, Australian and US Dollars, which all use the "$" symbol.

With the setting ``SHOP_MONEY_FORMAT`` we can style how money is going to be printed out. This
setting defaults to ``{symbol} {amount}``. The following format strings are allowed:

 * ``{symbol}``: The short symbol for a currency, for instance ``$``, ``£``, ``€``, ``¥``, etc.
 * ``{code}``: The international currency code, for instance USD, GBP, EUR, JPY, etc.
 * ``{currency}``: The spoken currency description, for instance “US Dollar”, “Pound Sterling”, etc.
 * ``{amount}``: The amount, unlocalized.

Thus, if we prefer to print ``9.98 US Dollar``, then we should set ``{amount} {currency}`` as the
formatting string.


Localizing Money
================

Depending on our current locale setting, amounts are printed using a localized format.


Money Database Fields
=====================

Money can be stored in the database, keeping the currency information together with the field type.
Internally, the database uses the Decimal type, but such a field knows its currency and will return
an amount as ``MoneyIn...`` type. This prevents implicit, but accidental currency conversions.

In our database model, declare a field as:

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

The default REST behavior serializes Decimal types as floats. This is fine if we want to do some
computations in the browser using JavaScript. However, then the currency information is lost and
must be re-added somehow to the output strings. It also is a bad idea to do commercial calculations
using floats, yet JavaScript does not offer any Decimal-like type. It therefore is recommended to
always do the finance arithmetic on the server and transfer amount information using JSON strings.
