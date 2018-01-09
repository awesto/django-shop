=======================
Building your own Views
=======================

Whenever we create a customized view in **django-SHOP**, we should use a View class as provided by
DjangoRestFramework, instead of using one of the many View classes provided by Django itself. This
keeps our Views consistent and allows us to reuse them as REST endpoints to communicate with client
code written in JavaScript.

Let's say, we need a View, which allows the modification of some product's attributes, rather than
just retrieving them. To render the product details, we typically use the built-in product's
detail view: :ref:`shop.views.catalog.ProductRetrieveView`.

Since we want to reuse that same view to *update* our product, we must
