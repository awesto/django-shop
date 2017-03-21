.. _howto/multi-tenancy:

=============
Multi-Tenancy
=============

If a site built with the **django-SHOP** framework shall be used by more than one vendor, we speak
about a multi-tenant environment. **Django-SHOP** does not implement multi-tenancy out of the box,
it however is quite simple to extend and customize.


Terminology
===========

To distinguish the roles in a multi-tenant environment, we define the *merchant* as the site owner.
On the other side, a *vendor* owns a range of products. Each new product, he adds to the site, is
assigned to him. Later on, existing products can only be modified and deleted by the vendor they
belong to.


Product Model
=============

Since we are free to declare our own product models, This can be achieved by adding a foreign key onto the User model:

.. code-block:: python

	from shop.models.product import BaseProduct

	class Product(BaseProduct):
	    # other product attributes
	    merchant = models.ForeignKey(
	        User,
	        verbose_name=_("Merchant"),
	        limit_choices_to={'is_staff': True},
	    )

.. note:: unfinished docs
