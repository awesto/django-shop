=======================
Routing to our Products
=======================

Now that we know how to create product models and how to administer them, lets have a look on how
to route them to our views. A nice aspect of **djangoSHOP** is, that it doesn't require the
programmer to write any special Django Views to render the products to be sold. Instead all
business logic shall go into their model classes, their model managers or into their serializers.


Product List Views
==================

Although in **djangoSHOP** it is possible to create explicit list views for products, even a simple
CMS page can used in combination with an apphook_.

When editing the CMS page used for the products list view, open **Advanced Settings** and chose
**Products List** from the select box labeled **Application**.

Use a template with at least one placeholder_. Click onto **View on site** to change into front-end
editing mode. Locate your main placeholder and add a **Row** followed by a **Column** plugin from
the section **Bootstrap**. Below that column add a **Catalog List Views** plugin from section
**Shop**. Then publish the page, it should not display any products yet.

.. _apphook: http://docs.django-cms.org/en/latest/how_to/apphooks.html
.. _placeholder: http://django-cms.readthedocs.org/en/latest/introduction/templates_placeholders.html#placeholders


Add products to the category
----------------------------

Open the detail view of a product in Django's administration backend. Locate the many-to-many
select box labeled **Categories / Cms pages**. Select the pages where each product shall appear
on.

On reloading the list view, the assigned products now shall be visible. Assure that they have been
set to be active.


Product Model Serializers
=========================

We already learned how to write model classes and model managers, so what are serializers for?
**DjangoSHOP** does not distinguish between list and detail views where the product information is
rendered as HTML or where the product data is transferred via JSON. This gives us the ability to
use the same business logic for web browsers as well as for native shopping applications.

Try to open the list- or detail view of one of your products. Now append ``?format=api`` or
``?format=json`` to the URL in the browser. This will render the pure product information, but
without embedding it into HTML.

