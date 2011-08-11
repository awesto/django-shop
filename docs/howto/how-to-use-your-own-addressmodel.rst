================================
How to use your own addressmodel
================================

(Instead of the default one)

Some people might feel like the current addressmodel is not suitable for their
project. You might be using a "client" + address model from an external application
or simply want to write your own.

This is a rather advanced use case, and most developers should hopefully be happy 
with the default model. It is however relatively easy to do.

Deactivate the default addressmodel
===================================

Simple enough: just remove or comment the corresponding entry in your project's
INSTALLED_APPS::

    INSTALLED_APPS = (
    ...
    'shop', # The django SHOP
    #'shop.addressmodel', # <-- Comment this out
    ...
    )
    

Hook your own model to the shop
================================

To achieve this, simply add a `SHOP_ADDRESS_MODEL` to your settings file, and
give the full python path to your Address model as a value::

    SHOP_ADDRESS_MODEL = 'myproject.somepackage.MyAddress'
    

Your custom model *must* unfortunately have the following two fields defined for
the checkout views to work::

    user_shipping = models.OneToOneField(User, related_name='shipping_address', blank=True, null=True)
    user_billing = models.OneToOneField(User, related_name='billing_address', blank=True, null=True)
    
This is to ensure that the views take handle "attaching" the address objects to the
User (or the session if the shopper is a guest).

We recommend to add :meth:`as_text` method to your address model that 'collects' all fields
and return them in one string. This string will be saved to order
(to :attr:`~shop.models.Order.billing_address_text` or
:attr:`~shop.models.Order.shipping_address_text` accordingly) during checkout view.
    
You are obviously free to subclass theses views and hook your own behavior.
