.. _howto/handling-taxes:

======
Taxes
======

As a general rule, the unit price of a product, shall always contain the net price. When our
products show up in the catalog, their method ``get_price(request)`` is consulted by the framework.
It is here where you add tax, depending on the tax model to apply. See below.


Use Cart Modifiers to handle Value Added Tax
============================================

**Django-SHOP** is not shipped with any kind of built-in tax handling code. This is because tax
models vary from product to product and region to region. Therefore the tax computation shall be
pluggable and easily exchangeable.


American tax model
------------------

The American tax model presumes that all prices are shown as net prices, hence the subtotal is the
sum of all net prices. On top of the subtotal we add the taxes and hence compute the total.

A simple tax cart modifier which adds the tax on top of the subtotal:

.. code-block:: python

	from shop.serializers.cart import ExtraCartRow
	from shop.modifiers.base import BaseCartModifier

	VALUE_ADDED_TAX = 9.0

	class CartIncludeTaxModifier(BaseCartModifier):
	    taxes = VALUE_ADDED_TAX / 100

	    def add_extra_cart_row(self, cart, request):
	        amount = cart.subtotal * self.taxes
	        instance = {
	            'label': "plus {}% VAT".format(VALUE_ADDED_TAX),
	            'amount': amount,
	        }
	        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
	        cart.total += amount


European tax model
------------------

The European tax model presumes that all prices are shown as gross prices, hence the subtotal
already contains the taxes. However, we must report the contained taxes on the invoice.

A simple tax cart modifier which reports the tax already included in the subtotal:

.. code-block:: python

	from shop.serializers.cart import ExtraCartRow
	from shop.modifiers.base import BaseCartModifier

	VALUE_ADDED_TAX = 19.0

	class CartExcludedTaxModifier(BaseCartModifier):
	    taxes = 1 - 1 / (1 + VALUE_ADDED_TAX / 100)

	    def add_extra_cart_row(self, cart, request):
	        amount = cart.subtotal * self.taxes
	        instance = {
	            'label': "{}% VAT incl.".format(VALUE_ADDED_TAX),
	            'amount': amount,
	        }
	        cart.extra_rows[self.identifier] = ExtraCartRow(instance)

Note that here we do not change the current total.

Mixed tax models
----------------

When doing business to business, then in Europe the American tax model is used. Sites handling both
private customers as well as business customers must provide a mixture of both tax models.
Since business customers can be identified through the ``Customer`` objects provided by ``request``
object, we can determine which tax model to apply in each situation.


Varying Taxes per Item
======================

For certain kind of products, different tax rates must be applied. If your e-commerce site must
handle these kinds of products, then we add a tag to our product model. This could be an enum field,
with one value per tax rate or a decimal field containing the rate directly.

In this example we use the latter, where each product contains a field named ``vat``, containing the
tax rate in percent.

.. code-block:: python

	from shop.serializers.cart import ExtraCartRow
	from shop.modifiers.base import BaseCartModifier
	from myshop.models.product import Product

	class TaxModifier(BaseCartModifier):
	    def __init__(self, identifier=None):
	        super(TaxModifier, self).__init__(identifier)
	        self.tax_rates = Product.objects.order_by('vat').values('vat').annotate(count=Count('vat'))

	    def pre_process_cart(self, cart, request):
	        for rate in self.tax_rates:
	            tax_attr = '_{}_vat_{vat}'.format(self.identifier, **rate)
	            setattr(cart, tax_attr, Money(0))

	    def add_extra_cart_item_row(self, cart_item, request):
	        vat = cart_item.product.vat
	        tax_attr = '_{0}_vat_{1}'.format(self.identifier, vat)
	        amount = cart_item.line_total * Decimal(vat) / 100
	        setattr(cart_item, tax_attr, amount)

	    def post_process_cart_item(self, cart, cart_item, request):
	        tax_attr = '_{0}_vat_{1}'.format(self.identifier, cart_item.product.vat)
	        setattr(cart, tax_attr, getattr(cart, tax_attr) + getattr(cart_item, tax_attr))

	    def add_extra_cart_row(self, cart, request):
	        for rate in self.tax_rates:
	            tax_attr = '_{}_vat_{vat}'.format(self.identifier, **rate)
	            instance = {
	                'label': "plus {vat}% VAT".format(**rate),
	                'amount': getattr(cart, tax_attr),
	            }
	            cart.extra_rows['{}:vat_{vat}'.format(self.identifier, **rate)] = ExtraCartRow(instance)

	    def process_cart(self, cart, request):
	        super(TaxModifier, self).process_cart(cart, request)
	        for rate in self.tax_rates:
	            tax_attr = '_{}_vat_{vat}'.format(self.identifier, **rate)
	            cart.total += getattr(cart, tax_attr)

First, in method ``pre_process_cart`` we add additional attributes to the cart object, in order to
have a placeholder where to sum up the taxes for each tax rate.

In method ``add_extra_cart_item_row`` we compute the tax amount for each item individually and store
it as additional attribute in each cart item.

In method ``post_process_cart_item`` we sum up the tax amount over all cart items.

In method ``add_extra_cart_row`` we report the sum of all tax rates individually. They will show up
on the invoice using one line per tax rate.

Finally, in method ``process_cart`` we sum up all tax amounts for all rates and add them to the
cart's total.
