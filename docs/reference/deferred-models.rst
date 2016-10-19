.. _reference/deferred-models:

======================
Deferred Model Pattern
======================

Until **django-SHOP** version 0.2, there were abstract and concrete and models: ``BaseProduct`` and
``Product``, ``BaseCart`` and ``Cart``, ``BaseCartItem`` and ``CartItem``, ``BaseOrder`` and
``Order`` and finally, ``BaseOrderItem`` and ``OrderItem``.

The concrete models were stored in ``shop.models``, whereas abstract models were stored in
``shop.models_bases``. This was quite confusing and made it difficult to find the right model
definition whenever one had to access the definition of one of the models.
Additionally, if someone wanted to subclass a model, he had to use a configuration directive, say
``PRODUCT_MODEL``, ``ORDER_MODEL``, ``ORDER_MODEL_ITEM`` from the projects ``settings.py``.

This made configuration quite complicate and causes other drawbacks:

* Unless *all* models have been overridden, the native ones appeared in the administration backend
  below the category *Shop*, while the customized ones appeared under the given project's name.
  To merchants, this inconsistency in the backend was quite difficult to explain.
* In the past, mixing subclassed with native models caused many issues with circular dependencies.

Therefore in **django-SHOP**, since version 0.9 *all* concrete models, ``Product``, ``Order``,
``OrderItem``, ``Cart``, ``CartItem`` have been removed. These model definitions now all are
abstract and named ``BaseProduct``, ``BaseOrder``, ``BaseOrderItem``, etc. They all have been moved
into the folder ``shop/models/``, because that's the location a programmer expects them.


Materializing Models
====================

Materializing such an abstract base model, means to create a concrete model with an associated
database table. This model creation is performed in the concrete project implementing the shop;
it must be done for each base model in the shop software.

For instance, materialize the cart by using this code snippet inside our own shop's
``models/shopmodels.py`` files:

.. code-block:: python

	from shop.models import cart

	class Cart(cart.BaseCart):
	    my_extra_field = ...

	    class Meta:
	        app_label = 'my_shop'

	class CartItem(cart.BaseCartItem):
	    other_field = ...

	    class Meta:
	        app_label = 'my_shop'

Of course, we can add as many extra model fields to this concrete cart model, as we wish.
All shop models, now are managed through *our* project instance. This means that the models
**Cart**, **Order**, etc. are now managed by the common database migrations tools, such as
``./manage.py makemigration my_shop`` and ``./manage.py migrate my_shop``. This
also means that these models, in the Django admin backend, are visible under **my_shop**.


Use the default Models
----------------------

Often we don't need extra fields, hence the abstract shop base model is enough. Then,
materializing the models can be done using some convenience classes as found in
``shop/models/defaults``. We can simply import them into ``models.py`` or ``models/__init__.py`` in
our own shop project:

.. code-block:: python

	from shop.models.defaults.cart import Cart  # nopyflakes
	from shop.models.defaults.cart_item import CartItem  # nopyflakes

.. note:: The comment ``nopyflakes`` has been added to suppress warnings, since these classes
		arern't used anywhere in ``models.py``.

All the configuration settings from **django-SHOP** <0.9: ``PRODUCT_MODEL``, ``ORDER_MODEL``,
``ORDER_MODEL_ITEM``, etc. are not required anymore and can safely be removed from our
``settings.py``.


Accessing the deferred models
=============================

Since models in **django-SHOP** are yet unknown during instantiation, one has to access their
materialized instance using the `lazy object pattern`_. For instance in order to access the Cart,
use:

.. code-block:: python

	from shop.models.cart import CartModel

	def my_view(request):
	    cart = CartModel.objects.get_from_request(request)
	    cart.items.all()  # contains the queryset for all items in the cart

Here ``CartModel`` is a lazy object resolved during runtime and pointing on the materialized, or,
to say it in other words, real Cart model.

.. _lazy object pattern: _https://docs.djangoproject.com/en/dev/_modules/django/utils/functional/


Technical Internals
===================

Mapping of Foreign Keys
-----------------------

One might argue, that this can't work, since foreign keys must refer to a real model, not to
abstract ones! Therefore one can not add a field ``ForeignKey``, ``OneToOneField`` or
``ManyToManyField`` which refers an abstract model in the **django-SHOP** project. But
relations are fundamental for a properly working software. Imagine a ``CartItem`` without a foreign
relation to ``Cart``.

Fortunately there is a neat trick to solve this problem. By deferring the mapping onto a real model,
instead of using a real ``ForeignKey``, one can use a special “lazy” field, declaring a relation
with an abstract model. Now, whenever the models are “materialized”, then these abstract relations
are converted into real foreign keys. The only drawback for this solution is, that one may derive
from an abstract model only once, but for **django-SHOP** that's a non-issue and doesn't differ from
the current situation, where one can subclass ``BaseCart`` only once anyway.

Therefore, when using this deferred model pattern, instead of using ``models.ForeignKey``,
``models.OneToOneField`` or ``models.ManyToManyField``, use the special fields
``deferred.ForeignKey``, ``deferred.OneToOneField`` and ``deferred.ManyToManyField``. When
Django materializes the model, these deferred fields are resolved into real foreign keys.


Accessing the materialized model
--------------------------------

While programming with abstract model classes, sometimes they must access their model manager
or their concrete model definition. A query such as ``BaseCartItem.objects.filter(cart=cart)``
therefore can not function and will throw an exception. To facilitate this, the deferred model's
metaclasses adds an additional member ``_materialized_model`` to their base class, while building
the model class. This model class then can be accessed through lazy evaluation, using ``CartModel``,
``CartItemModel``, ``OrderModel``, ``OrderItemModel``, etc.
