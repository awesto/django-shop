Using the deferred model pattern
================================

Until **django-shop** version 0.2, there were concrete and abstract models: ``BaseProduct`` and
``Product``, ``BaseCart`` and ``Cart``, ``BaseCartItem`` and ``CartItem``, ``BaseOrder``and ``Order``
and finally, ``BaseOrderItem`` and ``OrderItem``.

The concrete models were stored in ``shop.models``, whereas abstract models were stored in
``shop.models_bases``. This was quite confusing and made it difficult to find the right model
definition whenever one had to access the definition of one of the models.
Additionally, if someone wanted to override a model, he had to use a configuration directive, say
``PRODUCT_MODEL``, ``ORDER_MODEL``, ``ORDER_MODEL_ITEM`` from the projects ``settings.py``.

This made configuration quite complicate and causes other drawbacks:

* Unless *all* models have been overridden, the native ones appeared in the administration backend
  below the category **Shop**, while the customized ones appeared under the given project's name.
  To a customer, this backend inconsistency was quite difficult to explain.
* In the past, mixing overriden with native models caused many issues with circular dependencies.

Therefore in **django-shop**, since version 0.3 all concrete models, ``Product``, ``Order``, ``OrderItem``,
``Cart``, ``CartItem`` have been removed. These model definitions now all are abstract and named
``BaseProduct``, ``BaseOrder``, ``BaseOrderItem``, etc. They all have been moved into the folder
``shop/models/``, because this is the location a programmer expects them.

Materialize such an abstract base model, means to create a concrete model with associated database
table. This model creation is performed in the concrete shop implementation and must be done for
each base model in the shop software.

For instance, materialize the cart by using this code snippet inside your own shop's
``models/shopmodels.py`` files:

```
from shop.models import cart

class Cart(cart.BaseCart):
    pass


class CartItem(cart.BaseCartItem):
    pass
```

Of course, you can add as many extra model fields to this concrete cart model, as you wish.
All shop models, now are managed through your shop instance. This means that **Cart**, **Order**,
etc. models now all are managed by the common database migrations tools, such as
``./manage.py makemigration my_shop_instance`` and ``./manage.py migrate my_shop_instance``. This
also means that these models are visible under your shop's group in the admin interface.

Note, all the configuration settings ``PRODUCT_MODEL``, ``ORDER_MODEL``, ``ORDER_MODEL_ITEM``,
etc. are not required anymore and can safely be removed from **django-shop**.

For an application using **django-shop** this should not be a big deal. Each application simply
derives each model from one of the abstract base models and thus creates its concrete model.
This also avoids another problem, one might easily encounter: Say, one starts with **django-shop**
and uses the built-in ``Cart`` model. In the database this is handled by a table named ``shop_cart``.
Sometimes later, he decides to add an extra field to the model ``Cart``. He then has to create 
a customized cart model in his own application, but now the database table will have a different
name and it is not possible to override this using ``app_name`` in the model's ``Meta`` class.
These kinds of migration are not handled by South and therefore he has to write a migration for
renaming the table by hand.


Technical Details
=================

Mapping of Foreign Keys
-----------------------

One might argue, that this can't work, since foreign keys must refer to a real model, not to
abstract ones! Therefore one can not add a field ``ForeignKey``, ``OneToOneField`` or
``ManyToManyField`` which refers an abstract model in the **django-shop** project. However, these
relations are fundamental for a properly working software. Imagine a ``CartItem`` without a foreign
relation to ``Cart``.

Fortunately there is a neat trick to solve this problem. By deferring the mapping onto a real model,
instead of using a real ``ForeignKey``, one can use a special placeholder field defining a relation
with an abstract model. Now, whenever the models are “materialized”, then these abstract relations
are converted into real foreign keys. The only drawback for this solution is, that one may derive
from an abstract model only once, but that's a non-issue and doesn't differ from the current
situation, where one for instance, also can override ``Cart`` only once.

Therefore, when using this deferred model pattern, instead of using ``models.ForeignKey``,
``models.OneToOneField`` or ``models.ManyToManyField``, use the special pseudo-fields:
``DeferredForeignKey``, ``DeferredOneToOneField`` and ``DeferredManyToManyField``. During the
materialization of a model, these pseudo-fields are replaced against real foreign keys.


Accessing the materialized model
--------------------------------

While programming with abstract model classes, sometimes they require to access their model manager
or their concrete model definition. A query such as ``BaseCartItem.objects.filter(cart=cart)``
therefore will throw an exception. To facilitate this, the deferred model metaclasses add the
additional member ``MaterializedModel`` to their base class, while building the model class.
This field then can be accessed and used to perform the above query:
``BaseCartItem.MaterialzedModel.objects.filter(cart=cart)``.
