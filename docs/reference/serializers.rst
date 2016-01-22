.. _serializers:

================
REST Serializers
================

God application programming style is to strictly separate of *Models*, *Views* and *Controllers*.
In typical classic Django jargon, *Views* act as, what outsiders normally would denote a controller.

Controllers can sometimes be found on the server and sometimes on the client. In **djangoSHOP**
a significant portion of the controller code is written in JavaScript in the form of Angular
directives_.

Therefore, all data exchange between the *View* and the *Model* must be performed in a serializable
format, namely JSON. This allows us to use the same business logic for the server, as well as for
the client. It also means, that we could create native mobile apps, which communicate with a
web-application, without ever seeing a line of HTML code.


Every URL is a REST endpoint
============================

Every URL which is part of part of **djangoSHOP**, namely the product's list and detail views, the
cart and checkout views, the order list and detail views, they all are REST endpoints. What does
that mean?


Catalog List View
-----------------

Say, you are working with the provided demo shop, then the product's list view is available at
http://localhost:8000/de/shop/ . By appending ``?format=json`` to the URL, the raw data making up 
our product list, is rendered as a JSON object. For humans, this is difficult to read, therefore
the Django Restframework offers a version which is more legible: Instead of the above, invoke the
URL as http://localhost:8000/de/shop/?format=api . This renders the list of products as:

|rest-catalog-list|

.. |rest-catalog-list| image:: /_static/rest-catalog-list.png


Catalog Detail View
-------------------

By following a URL of a product's detail view, say
http://localhost:8000/de/shop/smart-phones/apple-iphone-5?format=api , one may check the legible
representation such as:

|rest-catalog-detail|

.. |rest-catalog-detail| image:: /_static/rest-catalog-detail.png


Add Product to Cart
-------------------

The product detail view requires another serializer, the so called ``AddToCartSerializer``. This
serializer is responsible for controlling the number of items being added to the cart and gives 
feedback on the subtotal of that potential cart item.

This serializer is slightly different than the previous ones, because it not only serializes
data and sends it from the server to the client, but it also deserializes data submitted from the
client back to the server using a post-request. This normally is the quantity, but in more
elaborated use cases, this could contain attributes to distinguish product variations. The
``AddSmartPhoneToCartSerializer``uses this pattern.

Since each product type may inherit from ``AddToCartSerializer``, and hence override its
functionality with a customized implementation, such a serializer may return any other information
relevant to the customer. This could for instance be a rebate or an availability update.


Routing to these endpoints
--------------------------

Since we are using CMS pages to display the catalog's list view, we must provide an apphook_ to
attach it to this page. These catalog apphooks are not part of the shop framework, but must be
created and configured by the project.



.. _directives: https://docs.angularjs.org/guide/directive
.. _apphook: http://django-cms.readthedocs.org/en/stable/introduction/apphooks.html