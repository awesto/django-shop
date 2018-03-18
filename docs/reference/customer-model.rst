.. _reference/customer-model:

==============
Customer Model
==============

Most web applications distinguish logged in users explicitly from *the* anonymous site visitor,
which is regarded as a non-existing user, and hence does not reference a session- or database
entity. The Django framework, in this respect, is no exception.

This pattern is fine for web-sites, which run a Content Management System or a Blog, where only an
elected group of staff users shall be permitted to access. This approach also works for
web-services, such as social networks or Intranet applications, where visitors have to authenticate
right on from the beginning of their session.

But when running an e-commerce site, this use-pattern has serious drawbacks. Normally, a visitor
starts to look for interesting products, hopefully adding a few of them to their cart. Then on the
way to checkout, they decide whether to create a user account, use an existing one or continue
as guest. Here's where things get complicated.

First of all, for non-authenticated site visitors, the cart does not belong to anybody. But each
cart must be associated with *its* current site visitor, hence the generic anonymous user object
is not appropriate for this purpose. Unfortunately the Django framework does not offer an explicit
but anonymous user object based on the assigned ``Session-Id``.

Secondly, at the latest when the cart is converted into an order, but the visitor wants to continue
as guest (thus remaining anonymous), that order object *must* refer to an user object in the
database. These kind of users would be regarded as *fakes*: Unable to log in, reset their password,
etc. The only information which must be stored for such a faked user, is their email address
otherwise they couldn't be informed, whenever the state of their order changes.

Django does not explicitly allow such user objects in its database models. But by using the boolean
flag ``is_active``, we can fool an application to interpret such a *guest visitor* as a faked
anonymous user.

However, since such an approach is unportable across all Django based applications, **django-SHOP**
introduces a new database model – the ``Customer`` model, which extends the existing ``User`` model.


Properties of the Customer Model
================================

The ``Customer`` model has a 1:1 relation to the existing ``User`` model, which means that for each
customer, there always exists *one and only one* user object. This approach allows us to do a few
things:

The built-in ``User`` model can be swapped out and replaced against another implementation. Such an
alternative implementation has a small limitation. It must inherit from
``django.contrib.auth.models.AbstractBaseUser`` and from ``django.contrib.auth.models.PermissionMixin``.
It also must define all the fields which are available in the default model as found in
``django.contrib.auth.models.User``.

By setting the flag ``is_active = False``, we can create guests inside Django's ``User`` model.
Guests can not sign in, they can not reset their password, and hence can be considered as
"materialized" anonymous users.

Having guests with an entry in the database, gives us another advantage: By using the session key
of the site visitor as the user object's ``username``, it is possible to establish a link between a
``User`` object in the database with an otherwise anonymous visitor. This further allows the
``Cart`` and the ``Order`` models always refer to the ``User`` model, since they don't have to care
about whether a certain user authenticated himself or not. It also keeps the workflow simple,
whenever an anonymous user decides to register and authenticate himself in the future.


Adding the Customer model to our application
============================================

As almost all models in **django-SHOP**, the ``Customer`` model itself, uses the
:ref:`reference/deferred-models`. This means that the Django project is responsible for
materializing that model and additionally allows the merchant to add arbitrary fields to *his*
``Customer`` model. Sound choices are a phone number, birth date, a boolean to signal whether the
customer shall receive newsletters, his rebate status, etc.

The simplest way is to materialize the given ``Customer`` class as found in our default and
convenience models:

.. code-block:: python

    from shop.models.defaults.customer import Customer

or, if we need extra fields, then instead of the above, we create a customized ``Customer`` model:

.. code-block:: python

    from shop.models.customer import BaseCustomer

    class Customer(BaseCustomer):
        birth_date = models.DateField("Date of Birth")
        # other customer related fields


Configure the Middleware
------------------------

A Customer object is created automatically with each visitor accessing the site. Whenever Django's
internal AuthenticationMiddleware_ adds an ``AnonymousUser`` to the request object, then the
**django-SHOP**'s CustomerMiddleware adds a ``VisitingCustomer`` to the request object as well.
Neither the ``AnonymousUser`` nor the ``VisitingCustomer`` are stored inside the database.

Whenever the AuthenticationMiddleware adds an instantiated ``User`` to the request object,
then the **django-SHOP**'s CustomerMiddleware adds an instantiated ``Customer`` to the request object
as well. If no associated ``Customer`` exists yet, the CustomerMiddleware creates one.

Therefore add the CustomerMiddleware *after* the AuthenticationMiddleware in the project's
``settings.py``:

.. code-block:: python

    MIDDLEWARE_CLASSES = (
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'shop.middleware.CustomerMiddleware',
        ...
    )

.. _AuthenticationMiddleware: https://docs.djangoproject.com/en/stable/ref/middleware/#django.contrib.auth.middleware.AuthenticationMiddleware


Configure the Context Processors
--------------------------------

Additionally, some templates may need to access the customer object through the ``RequestContext``.
Therefore, add this context processor to the ``settings.py`` of the project.

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'shop.context_processors.customer',
        ...
    )


Implementation Details
----------------------

The ``Customer`` model has a non-nullable one-to-one relation to the ``User`` model. Therefore each
customer is associated with exactly one user. For instance, accessing the hashed password can be
achieved through ``customer.user.password``. Some common fields and methods from the ``User`` model,
such as ``first_name``, ``last_name``, ``email``, ``is_anonymous()`` and ``is_authenticated()`` are
accessible directly, when working with a ``Customer`` object. Saving an instance of type
``Customer`` also invokes the ``save()`` method from the associated ``User`` model.

The other direction – accessing the ``Customer`` model from a ``User`` – does not always work.
Accessing an attribute that way fails if the corresponding customer object is missing, ie. if there
is no reverse relation from a ``Customer`` pointing onto the given ``User`` object.

.. code-block:: python

    >>> from django.contrib.auth import get_user_model
    >>> user = get_user_model().create(username='bobo')
    >>> print user.customer.salutation
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "django/db/models/fields/related.py", line 206, in __get__
        self.related.get_accessor_name()))
    DoesNotExist: User has no customer.

This can happen for ``User`` objects added manually or by other Django applications.

During database queries, **django-SHOP** always performs and INNER JOIN between the customer and the
user table. Therefore it performs better to query the ``User`` via the ``Customer`` object, rather
than vice versa.


.. _reference/visitors-guests-registered-customers:

Anonymous Users and Visiting Customers
--------------------------------------

Most requests to our site will be of anonymous nature. They will not send a cookie containing a
session-Id to the client, and the server will not allocate a session bucket. The middleware adds
a ``VisitingCustomer`` object associated with an ``AnonymousUser`` object to the request. These
two objects are not stored inside the database.

Whenever such an anonymous user/visiting customer adds *his first item to the cart*, **django-SHOP**
instantiates a user object in the database and associates it with a customer object. Such a
customer is considered as "unregistered" and invoking ``customer.is_authenticated()`` will return
``False``; here its associated ``User`` model is inactive and has an unusable password.


Guests and Registered Customers
-------------------------------

On the way to the checkout, a customer must declare himself, whether to continue as guest, to
sign in using an existing account or to register himself with a new account. In the former case
(customer wishes to proceed as guest), the ``User` object remains as it is: Inactive and with an
unusable password. In the second case, the visitor signs in using Django's default authentication
backends. Here the cart's content is merged with the already existing cart of that user object.
In the latter case (customer registers himself), the user object is recycled and becomes an active
Django ``User`` object, with a password and an email address.


Obviate Criticism
-----------------

Some may argue that adding unregistered and guest customers to the user table is an anti-pattern or
hack. So, what are the alternatives?

We could keep the cart of anonymous customers in the session store. This was the procedure used
until **django-SHOP** version 0.2. It however required to keep two different models of the cart,
one session based and one relational. Not very practical, specially if the cart model should be
overridable by the merchant's own implementation.

We could associate each cart models with a session id. This would require an additional field which
would be NULL for authenticated customers. While possible in theory, it would require a lot of code
which distinguishes between anonymous and authenticated customers. Since the aim of this software is
to remain simple, this idea was dismissed.

We could keep the primary key of each cart in the session associated with an anonymous user/customer.
But this would it make very hard to find expired carts, because we would have to iterate over all
carts and for each cart we would have to iterate over all sessions to check if the primary keys
matches. Remember, there is no such thing as an OUTER JOIN between sessions and database tables.

We could create a customer object which is independent of the user. Hence instead of having a
``OneToOneField(AUTH_USER_MODEL)`` in model ``Customer``, we'd have this 1:1 relation with a
nullable foreign key. This would require an additional field to store the session id in the customer
model. It also would require an additional email field, if we wanted guest customers to remain
anonymous users – what they actually are, since they can't sign in. Apart from field duplication,
this approach would also require some code to distinguish between unrecognized, guest and
registered customers. In addition to that, the administration backend would require two
distinguished views, one for the customer model and one for the user model.


Authenticating against the Email Address
========================================

Nowadays it is quite common, to use the email address for authenticating, rather than an explicit
account identifier. This in Django is not possible without replacing the built-in ``User`` model.
Since for an e-commerce site this authentication variant is rather important, **django-SHOP** is
shipped with an optional drop-in replacement for the built-in ``User`` model.

This ``User`` model is almost identical to the existing ``User`` model as found in
``django.contrib.auth.models.py``. The difference is that it uses the field ``email`` rather than
``username`` for looking up the credentials. To activate this alternative User model, add that
alternative authentication app to the project's ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = (
        'django.contrib.auth',
        'email_auth',
        ...
    )

    AUTH_USER_MODEL = 'email_auth.User'

.. note:: This alternative ``User`` model uses the same database table as the Django authentication
        would, namely ``auth_user``. It is even field-compatible with the built-in model and hence
        can be added later to an existing Django project.


Caveat when using this alternative User model
---------------------------------------------

The savvy reader may have noticed that in ``email_auth.models.User``, the email field is not
declared as unique. This by the way causes Django to complain during startup with:

.. code-block:: guess

    WARNINGS:
    email_auth.User: (auth.W004) 'User.email' is named as the 'USERNAME_FIELD', but it is not unique.
        HINT: Ensure that your authentication backend(s) can handle non-unique usernames.

This warning can be silenced by adding ``SILENCED_SYSTEM_CHECKS = ['auth.W004']`` to the project's
``settings.py``.

The reason for this is twofold:

First, Django's default ``User`` model has no unique constraint on the email field, so
``email_auth`` remains more compatible.

Second, the uniqueness is only required for users which actually can sign in. Guest users on the
other hand can not sign in, but *they may return someday*. By having a unique email field, the
Django application ``email_auth`` would lock them out and guests would be allowed to buy only once,
but not a second time – something we certainly do not want!

Therefore **django-SHOP** offers two configurable options:

* Customers can declare themselves as guests, each time they buy something. This is the default
  setting, but causes to have non-unique email addresses in the database.
* Customer can declare themselves as guests the first time they buys something. If someday they
  return to the site a buy a second time, they will be recognized as returning customer and must
  use a form to reset their password. This configuration is activated by setting
  ``SHOP_GUEST_IS_ACTIVE_USER = True``. It further allows us, to set a unique constraint on the
  email field.

.. note:: The email field from Django's built-in ``User`` model has a max-length of 75 characters.
	This is enough for most use-cases but violates RFC-5321_, which requires 254 characters. The
	alternative implementation uses the correct max-length.

.. _RFC-5321: http://tools.ietf.org/html/rfc5321#section-4.5.3


Administration of Users and Customers
-------------------------------------

By keeping the ``Customer`` and the ``User`` model tight together, it is possible to reuse the
Django's administration backend for both of them. All we have to do is to import and register the
customer backend inside the project's ``admin.py``:

.. code-block:: python

    from django.contrib import admin
    from shop.admin.customer import CustomerProxy, CustomerAdmin

    admin.site.register(CustomerProxy, CustomerAdmin)

This administration backend recycles the built-in ``django.contrib.auth.admin.UserAdmin``, and
enriches it by adding the Customer model as a ``StackedInlineAdmin`` on top of the detail page.
By doing so, we can edit the customer and user fields on the same page.


Summary for Customer to User mapping
====================================

This table summarizes to possible mappings between a Django ``User`` model [1]_ and the Shop's
``Customer`` model:

+---------------------------------------+-----------------------------------------+----------------+
| Shop's Customer Model                 | Django's User Model                     | Active Session |
+=======================================+=========================================+================+
| ``VisitingCustomer`` object           | ``AnonymousUser`` object                | No             |
+---------------------------------------+-----------------------------------------+----------------+
| Unrecognized ``Customer``             | Inactive ``User`` object with unusable  | Yes, but not   |
|                                       | password                                | logged in      |
+---------------------------------------+-----------------------------------------+----------------+
| ``Customer`` recognized as guest [2]_ | Inactive ``User`` with valid email      | Yes, but not   |
|                                       | address and unusable password           | logged in      |
+---------------------------------------+-----------------------------------------+----------------+
| ``Customer`` recognized as guest [3]_ | Active ``User`` with valid email address| Yes, but not   |
|                                       | and unusable, but resetable password    | logged in      |
+---------------------------------------+-----------------------------------------+----------------+
| Registered ``Customer``               | Active ``User`` with valid email        | Yes, logged in |
|                                       | address, known password, optional       | using Django's |
|                                       | salutation, first- and last names,      | authentication |
|                                       | and more                                | backend        |
+---------------------------------------+-----------------------------------------+----------------+

.. [1] or any alternative ``User`` model, as set by ``AUTH_USER_MODEL``.

.. [2] if setting ``SHOP_GUEST_IS_ACTIVE_USER = False`` (the default).

.. [3] if setting ``SHOP_GUEST_IS_ACTIVE_USER = True``.


Manage Customers
----------------

**Django-SHOP** is shipped with a special management command which informs the merchant about the
state of customers. In the project's folder, invoke on the command line:

.. code-block:: shell

    ./manage.py shop_customers
    Customers in this shop: total=20482, anonymous=17418, expired=10111, active=1068, guests=1997, registered=1067, staff=5.

Read these numbers as:

* Anonymous customers are those which added at least one item to the cart, but never proceeded to
  checkout.
* Expired customers are the subset of the anonymous customers, whose session already expired.
* The difference between guest and registered customers is explained in the above table.


Delete expired customers
........................

By invoking on the command line:

.. code-block:: shell

    ./manage.py shop_customers --delete-expired

This removes all anonymous/unregistered customers and their associated user entities from the
database, whose session expired. This command may be used to reduce the database storage
requirements.
