==================================
How to extend django SHOP models
==================================

(Instead of the default ones)

Some people might feel like the django SHOP models are not suitable for their
project, or want to extend functionality for their specific needs.

This is a rather advanced use case, and most developers should hopefully be happy 
with the default models. It is however relatively easy to do.

All models you can override have a corresponding setting, which should contain
the class path to the model you wish to use in its stead.

.. note:: While your models will be used, they will still be "called" by their
  default django SHOP name.
  
Example
========

Extending the Product model in django SHOP works like this::
    
    # In myproject.models
    from shop.models_bases import BaseProduct
    class MyProduct(BaseProduct):
        def extra_method(self):
            return 'Yay'

        class Meta:
            pass
            
    # In your project's settings.py, add the following line:
    SHOP_PRODUCT_MODEL = 'myproject.models.MyProduct'

.. important:: Your model replacement must define a :class:`Meta` class.
   Otherwise, it will inherit its parent's :class:`Meta`, which will break
   things. The :class:`Meta` class does not need to do anything important - it
   just has to be there.

.. note:: The above example is intentionally *not* using the same module as
   the examples given earlier in this documentation (myproject versus
   myshop).  If MyProduct and Book were defined in the same module a circular 
   import will result culminating in an error similar to:
   ``django.core.exceptions.ImproperlyConfigured: Error importing backend
   myshop.models: "cannot import name Product". Check your SHOP_PRODUCT_MODEL
   setting``.
    
From a django interactive shell, you should now be able to do::

    >>> from shop.models import Product
    >>> p = Product.objects.all()[0] # I assume there is already at least one
    >>> p.extra_method()
    Yay
    >>> p.__class__
    <class object's class>
    
Settings
=========

All available settings to control model overrides are defined in :doc:`/settings`
