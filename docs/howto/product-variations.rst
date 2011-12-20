How to add variations to a product
==================================

Introduction
------------
django-shop ships with an additional module (django-shop_simplevariations) to
add two kind of variations: 'option group' and 'text option'. This module can
be used as an add on for any kind of product.

By using the built-in variation, the product model itself may specify any kind

add two kind of variations, an option group and a text option. As an add on, 
this module can be used for any kind of product.
By using the built-in variations, the product model itself may specify any kind
of thinkable variations. This variation model transparently integrates into the
checkout process of the shop.

The benefits for built-in variations:
- The variation definition is part of the product model.
- Any kind of information can be stored together with the product.
- Identical variations are always serialized to the same string, so identical
  product variations will sum up in CartItem, whereas different variations of 
  the same product create individual CartItem entries.
- A customer may readd an already shipped item from the list of orders to the 
  cart.
- The product model must not deal with problems, such as adding variation
  details to the CartItem, OrderItem or an external WishItem.

When using the django-shop-wishlists, built-in variations are a required 
feature.

Installation
------------
From Github install Picklefield
https://github.com/shrubberysoft/django-picklefield.git

Usage
-----
As a simple example, your product shall display a chooser for different colors.

Add one or more variations to your product model::
    

