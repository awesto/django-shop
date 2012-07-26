===============================
How to interact with the cart
===============================

Interacting with the cart is probably the single most important
thing shop implementers will want to do: e.g. adding products to it, changing
quantities, etc...

There are roughly two different ways to interact with the cart: through Ajax, or
with more standard post-and-refresh behavior.


Updating the whole cart
========================

The normal form POST method is pretty straightforward - you simply POST to the cart's
update URL (shop/cart/update/ by default) and pass it parameters as: update_item-<item id>=<new quantity>
Items corresponding to the ID will be updated with the new quantity


Emptying the cart
==================

Posting to shop/cart/delete empties the cart (the cart object is the same, but all cartitems are removed from
it)

