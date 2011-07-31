==================================
How to extend django-SHOP models
==================================

(Instead of the default ones)

Some people might feel like the django shop models are not suitable for their
project, or want to extend functionality for their specific needs.

This is a rather advanced use case, and most developers should hopefully be happy 
with the default models. It is however relatively easy to do.

All models you can override have a corresponding setting, which should contain
the class path to the model you wish to use in its stead.

.. note:: While your models will be used, they will still be "called" by their
  default django-SHOP name.
  
Example
========

Extending the Product model in django-SHOP works like this::
    
    # In myproject.models
    from shop.models import Product
    class MyProduct(BaseProduct):
        def extra_method(self):
            return 'Yay'

        class Meta:
            pass
            
    # In your project's settings.py, add the following line:
    SHOP_PRODUCT_MODEL = 'myproject.models.MyProduct'

.. important:: Your model replacement must define a :class:`Meta` class.
   Otherwise, they will inherit their parent's :class:`Meta`, which will break
   things. The :class:`Meta` class does not need to do anything important - it
   just has to be there.
    
From a django interactive shell, you should now be able to do::

    >>> from shop.models import Product
    >>> p = Product.objects.all()[0] # I assume there is already at least one
    >>> p.extra_method()
    Yay
    >>> p.__class__
    <class object's class>
    
Settings
=========

All available settings to control models overrides are defined in :doc:`/settings`
