============
Architecture
============

This document should gather all the pre-code architecture requirements/research.

Core system
===========

Generally, the shop system can be seen as two different phases, with two different problems to solve:

The shopping phase:
-------------------

From a user perspective, this is where you shop around different product categories, and add desired products to
a shopping cart (or other abstraction). This is a very well-know type of website problematic from a user interface
perspective as well as from a model perspective: a simple "invoice" pattern for the cart is enough.

The complexity here is to start defining what a shop item should be.

The checkout process:
---------------------

As the name implies, this is a "workflow" type of problem: we must be able to add or remove steps to the checkout process depending
on the presence or absence of some plugins.
For instance, a credit-card payment plugin whould be able to insert a payment details page with credit card details in the general workflow.

To solve this we could implement a workflow engine. The person implementing the webshop whould then define the process using
the blocks we provide, and the system should then "run on its own".


Random ideas:
-------------

* class-based views
* class based plugins (not modules based!)


Plugin structure
================

As suggested by fivethreeo::

# djangoshop/checkout.py

class CheckoutSite(object):
    """ code copied from AdminSite """
    pass

def autodiscover():
    pass

# djangoshop/__init__.py

from djangoshop.checkout import CheckoutSite
checkoutsite = CheckoutSite()

# djangoshop/shipper_base.py

class ShipperBase(object)
    pass
    
# djangoshop/payment_base.py

class PaymentBase(object)
    pass

# app/djangoshop_shipper.py

from djangoshop.shipper_base import ShipperBase

class ShipmentClass(ShipperBase):
    pass
    
checkoutsite.register_shipment(ShipmentClass)

# app/djangoshop_payment.py

from djangoshop.payment_base import PaymentBase

class PaymentClass(PaymentBase):
    pass
    
checkoutsite.register_payment(PaymentClass)
