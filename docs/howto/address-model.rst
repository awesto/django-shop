.. _howto/address-model:

=============
Address Model
=============

**DjangoSHOP** is shipped with a default address model as found in
:class:`shop.models.defaults.address.ShippingAddress` and
:class:`shop.models.defaults.address.BillingAddress`. It is based on a recommendation on
`International Address Fields in Web Forms`_.

Some people might feel that this address model is not suitable for their specific use-case, or in
their selling region. Since **django-SHOP** allows to override each model, we simply might want to
write our own one.

.. _International Address Fields in Web Forms: http://www.uxmatters.com/mt/archives/2008/06/international-address-fields-in-web-forms.php


Overriding the Default Models
=============================

To start with, have a look at the implementation of the default address models mentioned before.
Chances are high that you might want to use the same address model for shipping, as well as for
billing. Therefore instead of writing them twice, we use a mixin class:

.. code-block:: python

	from django.db import models

	class AddressModelMixin(models.Model):
	    name = models.CharField("Full name", max_length=1024)
	    address1 = models.CharField("Address line 1", max_length=1024)
	    address2 = models.CharField("Address line 2", max_length=1024, blank=True, null=True)
	    zip_code = models.CharField("ZIP", max_length=12)
	    city = models.CharField("City", max_length=1024)

	    class Meta:
	        abstract = True

This mixin class then is used to instantiate the billing address models:

.. code-block:: python

	from shop.models.address import BaseShippingAddress, BaseBillingAddress

	class BillingAddress(BaseBillingAddress, AddressModelMixin):
	    class Meta:
	        verbose_name = "Billing Address"

In Europe for B2B commerce, the customer's tax number is associated with the location for delivery.
We therefore have to add it to our shipping address models:

	class ShippingAddress(BaseShippingAddress, AddressModelMixin):
	    tax_number = models.CharField("Tax number", max_length=100)

	    class Meta:
	        verbose_name = "Shipping Address"


Multiple Addresses
==================

Depending on the shop's requirements, each customer may have no, one or multiple billing- and/or
shipping addresses. On an e-commerce site selling digital goods, presumably only the billing address
makes sense. A shop with many returning customers probably wants to allow them to store more than
one address.

In **django-SHOP** each address model has a foreign key onto the customer model, hence all of the
above use-cases are possible.


Rendering the Address Forms
===========================

During checkout
