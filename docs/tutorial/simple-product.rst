.. _simple-product:

=========================
Modeling a Simple Product
=========================

As a simple example, this tutorial uses Smart Cards as its first product. As emphasized in section
:ref:`customer-model`, **djangoSHOP** is not shipped with ready to use product models. Instead the
merchant must declare these models based on the products properties. Lets have a look ar a model
describing a typical Smart Card:

.. literalinclude:: /../example/myshop/models/simple/smartcard.py
	:caption: myshop/models/simple/smartcard.py
	:linenos:
	:language: python
	:lines: 10-12, 14-18, 21-29

Here our model ``SmartCard`` inherits directly from ``BaseProduct``, which is a stub class, hence
the most common fields, such as ``name``, ``slug`` and ``unit_price`` must be added to our product
here. Later on we will see why these fields, even though required by each product, can not be part
of our abstract model ``BaseProduct``.

Additionally a smart card has some product specific properties:

.. literalinclude:: /../example/myshop/models/simple/smartcard.py
	:linenos:
	:language: python
	:lines: 23-31

these class attributes depend heavily on the data sheet of the product to sell.

Finally we also want to position our products into categories and sort them:

.. literalinclude:: /../example/myshop/models/simple/smartcard.py
	:linenos:
	:language: python
	:lines: 32-36

The field ``order`` is used to keep track on the sequence of our products while rendering a list
view.

The field ``cms_pages`` specifies on which pages of the CMS a product shall appear.

.. note:: If categories do not require any technical properties, it often is completely
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

Additionally each product model requires these callables:

* A property method ``product_name``: Returns the product's name in its natural language.
* A property method ``product_code``: Returns a language independent product code or article number.
* An optional property method ``sample_image``: Returns a sample image for the given product.
* A method ``get_price(request)``: Returns the product price. This can depend on the given region,
  which is available through the request object.
* A method ``get_absolute_url()``: Returns the canonical URL of a product.


Add Model ``myshop.SmartCard`` to Django Admin
==============================================

For reasons just explained, it is the responsibility of the project to manage the many-to-many
relations between its CMS pages and the images on one side, and the product on the other side.
Therefore we can't use the built-in admin widget ``FilteredSelectMultiple`` for these relations.

Instead **djangoSHOP** is shipped with a special mixin class ``CMSPageAsCategoryMixin``, which
handles the relation between CMS pages and the product. This however implies that the field used
to specify this relation is named ``cms_pages``.

.. literalinclude:: /../example/myshop/admin/simple/smartcard.py
	:linenos:
	:language: python
	:lines: 6-

For images, the admin class must use a special inline class named ``ProductImageInline``. This is
because the merchant might want to arrange the order of the images and therefore a simple
``SelectMultiple`` widget won't do this job here.
