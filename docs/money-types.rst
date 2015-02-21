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

By calling ``MoneyMaker()`` a type accepting amounts in the default currency is created. The default
currency can be changed in ``settings.py`` with ``SHOP_DEFAULT_CURRENCY = 'USD'``, using one of the
official ISO-4217 currency codes.

Alternatively, you can create your own money type, for example ``Yen``.
