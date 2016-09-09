.. _tutorial/simple-product:

=========================
Modeling a simple product
=========================

As a simple example, this tutorial uses Smart Cards as its first product. As
emphasized earlier, **djangoSHOP** is not shipped with ready to use product
models.  Instead the merchant must declare these models based on the products
properties. Lets have a look ar a model describing a typical Smart Card:

.. literalinclude:: /../example/myshop/models/smartcard.py
	:caption: myshop/models/smartcard.py
	:linenos:
	:language: python
	:lines: 8-11, 15-22, 40-41

Here our model ``SmartCard`` inherits directly from ``BaseProduct``, which is a stub class, hence
the most common fields, such as ``product_name``, ``slug`` and ``unit_price`` must be added to our
product here. Later on we will see why these fields, even though required by each product, can not
be part of our abstract model ``BaseProduct``.

Additionally a smart card has some product specific properties:

.. literalinclude:: /../example/myshop/models/smartcard.py
	:linenos:
	:language: python
	:lines: 23-34

these class attributes depend heavily on the data sheet of the product to sell.

Finally we also want to position our products into categories and sort them:

.. literalinclude:: /../example/myshop/models/smartcard.py
	:linenos:
	:language: python
	:lines: 34-40

The field ``order`` is used to keep track on the sequence of our products while rendering a list
view.

The field ``cms_pages`` specifies on which pages of the CMS a product shall appear.

.. note:: If categories do not require to keep any technical properties, it often is completely
	sufficient to use CMS pages as their surrogates.

Finally ``images`` is another many-to-many relation, allowing to associate none, one or more images
to a product.

Both fields ``cms_pages`` and ``images`` must use the through_ parameter. This is because we have
two many-to-many mapping tables which are part of the merchant's project rather than the
**djangoSHOP** application. The first of those mapping tables has foreign keys onto the models
``cms.Page`` and ``myshop.SmartCard``. The second table has foreign keys onto the models
``filer.Image`` and ``myshop.SmartCard`` again. Since the model ``myshop.SmartCard`` has been
declared by the merchant himself, he also is responsible for managing those many-to-many mapping
tables.

.. _through: https://docs.djangoproject.com/en/stable/ref/models/fields/#django.db.models.ManyToManyField.through

Additionally each product model requires these attributes:

* A model field or property method named ``product_name``: It must returns the product's name in
  its natural language.
* A method ``get_price(request)``: Returns the product price. This can depend on the given region,
  which is available through the request object.
* A method ``get_absolute_url()``: Returns the canonical URL of a product.
* The ``object`` attribute must be of type ``BaseProductManager`` or derived from thereof.

These product model attributes are optional, but highly recommended:

* A model field or property method named ``product_code``: It shall returns a language independent
  product code or article number.
* A property method ``sample_image``: It shall returns a sample image for the given product.


Add Model ``myshop.SmartCard`` to Django Admin
==============================================

For reasons just explained, it is the responsibility of the project to manage the many-to-many
relations between its CMS pages and the images on one side, and the product on the other side.
Therefore we can't use the built-in admin widget ``FilteredSelectMultiple`` for these relations.

Instead **djangoSHOP** is shipped with a special mixin class ``CMSPageAsCategoryMixin``, which
handles the relation between CMS pages and the product. This however implies that the field used
to specify this relation is named ``cms_pages``.

.. literalinclude:: /../example/myshop/admin/smartcard/smartcard.py
	:linenos:
	:language: python
	:lines: 6-

For images, the admin class must use a special inline class named ``ProductImageInline``. This is
because the merchant might want to arrange the order of the images and therefore a simple
``SelectMultiple`` widget won't do this job here.


Extend our simple product to support other natural languages by
:ref:`tutorial/multilingual-product`.
