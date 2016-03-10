.. reference/configuration:

==========================
Configuration and Settings
==========================

The **djangoSHOP** framework itself, requires only a few configuration directives. However, since
each e-commerce site built around **djangoSHOP** consists of the merchant's own project, plus a
collection of third party Django apps, here is a summary of mandatory and some optional
configuration settings:


DjangoSHOP settings
===================

App Label
---------

.. code-block:: python

	SHOP_APP_LABEL = 'myshop'


Currency
--------

Unless Money types are specified explicitly, each project requires a default currency:

.. code-block:: python

	SHOP_DEFAULT_CURRENCY = 'EUR'

The typical format to render an amount is ``$ 1.23``, but some merchant may prefer ``1.23 USD``.
With:

.. code-block:: python

	SHOP_MONEY_FORMAT = '{symbol} {amount}'

we my specify our own money rendering format, where ``{symbol}`` is €, $, £, etc. and ``{currency}``
is EUR, USD, GBP, etc.


Cart Modifiers
--------------

Each project requires at least one cart modifier in order to initialize the cart. In most
implementations :class:`shop.modifiers.defaults.DefaultCartModifier` is enough, but depending
on the product models, the merchant's may implement an alternative.

To identify the taxes in the cart, use one of the provided tax modifiers.

Other modifiers may add extra payment and shipping costs, or rebate the total amount depending
on whatever appropriate.

.. code-block:: python

	SHOP_CART_MODIFIERS = (
	    'shop.modifiers.defaults.DefaultCartModifier',
	    'shop.modifiers.taxes.CartExcludedTaxModifier',
	    # other modifiers
	)

For further information, please refer to the :ref:`reference/cart-modifiers` documentation.


Workflow Mixins
---------------

.. code-block:: python

	SHOP_ORDER_WORKFLOWS = (
	    'shop.payment.defaults.PayInAdvanceWorkflowMixin',
	    'shop.payment.defaults.CommissionGoodsWorkflowMixin',
	    # other workflow mixins
	)


Editing the Cart
----------------

	SHOP_EDITCART_NG_MODEL_OPTIONS = "{updateOn: 'default blur', debounce: {'default': 2500, 'blur': 0}}"


.. note:: unfinished document

