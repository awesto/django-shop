.. _howto/multi-tenancy:

=============
Multi-Tenancy
=============

If a site built with the **djangoSHOP** framework shall be used by more than one merchant, then we
must associate each product with our merchants. This can be achieved by adding a foreign key onto
the User model:

..code-block:: python

	from shop.models.product import BaseProduct

	class Product(BaseProduct):
	    # other product attributes
	    merchant = models.ForeignKey(User, verbose_name=_("Merchant"),
	        limit_choices_to={'is_staff': True})

.. note:: unfinished docs
