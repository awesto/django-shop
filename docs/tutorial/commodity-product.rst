.. _tutorial/product-model-commodity:

===========================
The Commodity Product Model
===========================

The demo provided by `cookiecutter-django-shop`_ using the product model "commodity", shows how to
setup a shop, with a single generic product, named **Commodity**. The product model
:class:`shop.models.defauls.commodity.Commodity` is part of the **django-SHOP** framework. It is
intended for shops where the merchant does not want to create a customized product model, but
rather prefers to create the product's detail views using common CMS functionality. Here for
demonstration purpose we try to sell a house, hence it is practical that we can layout our CMS page
the way we want to and we can add whatever Django-CMS plugins are available.

A **Commodity** model contains only the following properties:

* The name of the product.
* The product code.
* The slug_ (a short label used as the last bit in the URLs).
* The product's unit price.
* One sample image to be shown in the catalog's list view.
* A caption to be shown in the catalog's list view.

The detail view for each product shall however be styled individually using a **django-CMS**
placeholder together with the plugin system provided, for instance by djangocms-cascade_. This
gives the merchant all the flexibility to style each product's detail page individually and without
having to create a special HTML template. It is thus best suited for types of products with a high
degree of customization. Hence in the demo, a house was used to show a product detail page, filled
with standard components from the CMS. Into this placeholder we then can add as many text fields as
we want. Additionally we can use image galleries, carousels, different backgrounds, tab sets, etc.

The ``commodity`` demo contains just one product, a splendid villa. In such a situation, we usually
don't want to render the catalogs list view with one item, but instead want to get redirected onto
our lonely product. This can be achieved by reconfiguring the catalogs list view, and is explained
in the reference sections.

Using the **Commodity** product model only makes sense, if the merchant does not require special
product properties and normally is only suitable for shops with up to a dozen articles. Otherwise,
creating a reusable HTML template is probably less effort, than filling the placeholder for each
product's detail page individually.

.. _cookiecutter-django-shop: https://github.com/awesto/cookiecutter-django-shop
.. _djangocms-cascade: https://djangocms-cascade.readthedocs.io/en/latest/
.. _slug: https://docs.djangoproject.com/en/stable/ref/models/fields/#slugfield


The Base Template
=================

Even though we can show the complete information about a (Commodity-) product using standard
components, provided by **django-CMS** and/or **djangocms-cascade**, we still have to provide a base
template with a placeholder. Since the **django-SHOP** framework doesn't want to know anything about
the skeleton of a page, this base template must be contributed by the merchant implementation.

On the assumption that the product's detail view renders a product of type "Commodity",
**django-SHOP** looks for a template named

#. ``myshop/catalog/commodity-detail.html``
#. if not found, then ``myshop/catalog/product-detail.html``
#. if not found, then ``shop/catalog/product-detail.html``

Note that all names are lowercased, while searching for the matching template. Such a base template
must contain the templatetag

.. code-block:: django

	{% load cms_tags %}
	…
	{% render_placeholder product.placeholder %}

Here the placeholder is a special field :class:`cms.models.fields.PlaceholderField` in our Django
model ``Commodity``. It is the equivalent to the placeholder otherwise used in regular
**django-CMS** page templates. This placeholder field can be added to all Django models for any
other product type and is useful, in case the merchant wants to add some optional and/or
unstructured information to its product model. This for instance, can be specially convenient to
add a video, a downloadable datasheet, or other useful information about the product.


.. _tutorial/product-model-i18n_commodity:

The Internationalized Commodity Product Model
=============================================

If support for multiple languages is enabled, some of the properties can be translated into
different natural languages. In the demo for the product model "commodity", these properties
then become translatable:

* The name of the product.
* The slug.
* A caption to be shown in the catalog's list view.

Using this internationalized version, requires to configure ``I18N = True`` in the ``settings.py``
of the project. Additionally, the thrird party app django-parler_ must be installed. By doing so,
the product model from above :class:`shop.models.defauls.commodity.Commodity`, is replaced by an
internationalized version.

All other product properties, such as unit price and product code are shared across all languages.

.. _django-parler: https://django-parler.readthedocs.io/en/latest/

.. _tutorial/commodity-add-to-cart:

Add Commodity to Cart
=====================

One plugin which should always be present on a product's detail page, is the
**Add Product to Cart**, as found in section **Shop**. Otherwise a customer wouldn't be able to
purchase that product. In the provided demo, we sell one house, hence the usual quantity doesn't
make sense. By using a slightly modified template, the quantity fields is hidden.

It often makes sense to override the "add-to-cart" template for special product models. If for
instance a product has variantions, this is where we would add additional choice fields so that the
customer can select different properties, such as size, color, etc.


Next Chapter
============

In the next chapter of this tutorial, we will see how to organize the :ref:`tutorial/cart-checkout`
