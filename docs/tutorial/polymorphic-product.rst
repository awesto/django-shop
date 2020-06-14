.. _tutorial/product-model-polymorphic:

=============================
The Polymorphic Product Model
=============================

The demo provided by cookiecutter-django-shop_ using the product model "polymorphic", shows how to
setup a shop, with different product types. This is where polymorphism_ enters the scene. In our
example we use a combination from the simpler demos "commodity" and "smartcard".

.. _cookiecutter-django-shop: https://github.com/awesto/cookiecutter-django-shop
.. _polymorphism: https://en.wikipedia.org/wiki/Polymorphism_(computer_science)

Since in this example, we have to specialize our product out of a common base, the properties for
each product type are shared accross two models. In our demo, the base model is declared by the
class :class:`myshop.models.Product`. Here we store the properties common to all product types,
such as the product's name, a caption, etc.

The model classes for Smart Card, Smart Phone and a variation of Commodity then inherits from this
base product class. These models additionally declare their model fields, which are required to
describe the physical properties of each product type. Since they vary, we also have to create
special templates for the detail views of each of them. Smart Phones for instance allow product
variations, therefore we must adopt the template for adding the product to the cart.


.. _tutorial/product-model-i18n_polymorphic:

The Internationalized Polymorphic Product Model
===============================================

The ``i18n_polymorphic`` demo is a variation of the above example, with a few attributes translated
into multiple languages, namely ``caption`` and ``description``. This sample implementation does not
use translated slugs, although it would be possible.


Next Chapter
============

In the next chapter of this tutorial, we will see how to organize the :ref:`tutorial/cart-checkout`
