==================
The Customer Model
==================

Most web applications distinguish logged in users explicitly from *the* anonymous site visitor,
which is regarded as a non-existing user, and thus is not referenced by a database entity. The
Django framework, in this respect, is no exception.

This pattern is fine for web-sites, which run a Content Management System or a Blog, where only an
elected group of staff users shall be permitted to access. This approach also works for
web-services, such as social networks or Intranet applications, where the visitors have to
authenticate right from the beginning.

But when running an e-commerce site, this use-pattern has serious drawbacks. Normally, a visitor
starts to look for interesting products, hopefully adding a few to his cart. Then on the way to the
checkout, he decides whether to create a user account, use an existing one or continue as guest.
Here things get complicated.

First of all, for non authenticated site visitors, the cart does not belong to anybody. But each
cart must be associated with its site visitor, hence the generic anonymous user object is not
appropriate for this purpose. Unfortunately the Django framework does not offer an explicit but
anonymous user object based on its session-id.

Secondly, at the latest when the cart is converted into an order, but the visitor wants to continue
as guest (thus remaining anonymous), that order object *must* refer to a user object in the
database. These kind of users would be regarded as fakes, unable to log in, reset their password,
etc. The only information which must be stored for such a faked user, is her email address otherwise
she couldn't be informed, whenever the state of her order changed.

Django does not explicitly allow such users in its database models. But by using the boolean flag
``is_active``, we can fool an application to interpret such a *guest visitor* as a faked anonymous
user. 

Since such an approach is unportable across all Django based applications, **djangoSHOP** introduces
a new database model – the ``Customer`` model, which extends the existing ``User`` model.


Properties of the Customer Model
================================

The ``Customer`` model has a 1:1 relation to the existing ``User`` model, which means that for each
customer, there always exists one and only one user object. This approach allows us to do a few
things:

The built-in User object can be swapped out and replaced against another implementation. Such an
alternative implementation has a small limitation. It must inherit from
``django.contrib.auth.models.AbstractBaseUser`` and from ``django.contrib.auth.models.PermissionMixin``.
It also must define all the fields, which are available in the default model as found in
``django.contrib.auth.models.User``.

By setting the flag ``is_active = False``, we can create guests inside Django's ``User`` model.
Guests can not sign, they can not reset their password and can thus be considered as “materialized”
anonymous users.

Having guests with an entry in the database, gives us another advantage: By storing the session key
of the site visitor inside the User object, it is possible to establish a connection between a User
object in the database with an otherwise anonymous visitor. This further allows the Cart and the
Order models always refer to the User model, since they don't  have to care about whether this user
authenticated or not. It also keeps the workflow simple, whenever an anonymous user decides to
register and authenticate himself.


Add the Customer model to your application
==========================================

As almost all models in ***djangoSHOP*, the Customer itself is deferrable_. This means that
the Django project is responsible for materializing that model. This allows the merchant to add
arbitrary fields to the Customer model. Good choices are a phone number, a boolean to signal whether
the customer shall receive newsletters, his rebate status, etc.

The simplest way is to materialize the given convenience class in your project's ``models.py``:

.. code-block:: python

	from shop.models.defaults.customer import Customer

or, if you needs extra fields, then instead of the above, do:

.. code-block:: python

	from shop.models.customer import BaseCustomer

	class (BaseCustomer):
	    birth_date = models.DateField("Date of Birth")
	    # other customer related fields

.. _deferrable: deferred-models


Configure the Middleware
------------------------

A Customer object is created automatically with each visitor accessing the site. Whenever Django's
internal AuthenticationMiddleware_ adds an ``AnonymousUser`` to the request object, djangoSHOP's
CustomerMiddleware adds a ``VisitingCustomer`` to the request object as well. Both, the
``AnonymousUser`` and the ``VisitingCustomer``, are not stored inside the database.

Whenever the AuthenticationMiddleware adds an instantiated ``User`` to the request object,
djangoSHOP's CustomerMiddleware adds an instantiated ``Customer`` to the request object
as well. If no associated ``Customer`` yet exists, the CustomerMiddleware creates one.

Therefore you must add the CustomerMiddleware after the AuthenticationMiddleware in the project's
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
Therefore, in the ``settings.py`` of your application, add this context processor:

.. code-block:: python

	TEMPLATE_CONTEXT_PROCESSORS = (
	    ...
	    'shop.context_processors.customer',
	    ...
	)


Implementation Details
----------------------

The Customer model has a non-nullable one-to-one relation to the User model. Therefore, each
Customer is associated with exactly one one User. For instance, accessing the hashed password can
be achieved through ``customer.user.password``. Some common fields and methods from the User model,
such as ``first_name``, ``last_name``, ``email``, ``is_anonymous()`` and ``is_authenticated()`` are
accessible directly, when working with a Customer object. Saving an instance of type Customer, also
invokes method ``save()`` from the associated User model.

The other direction – accessing the Customer model from a User – does not always work. Accessing
an attribute that way, fails if the corresponding Customer object is missing, ie. if no Customer
points onto the given User object.

.. code-block:: python

	>>> from django.contrib.auth import get_user_model
	>>> user = get_user_model().create(username='bobo')
	>>> print user.customer.salutation
	Traceback (most recent call last):
	  File "<console>", line 1, in <module>
	  File "django/db/models/fields/related.py", line 206, in __get__
	    self.related.get_accessor_name()))
	DoesNotExist: User has no customer.

This can happen for Users objects added by other applications than **djangoSHOP**.


Anonymous Users and Visiting Customers
--------------------------------------

Most requests to your site will be of anonymous nature. They will not send a cookie containing a
session_id to the client, and they won't create a session object on the server. Such requests
contain a ``VisitingCustomer`` object associated with an ``AnonymousUser`` object.

Whenever such an anonymous user/visiting customer adds the first item to the cart, djangoSHOP
instantiates a User object in the database and associates it with a Customer object. Such a
Customer is considered as “unregistered” and invoking ``customer.is_authenticated()`` will return
False; its associated User model is inactive and has an unusable password.

On the way the the checkout, a customer must declare himself, whether to continue as guest, to
sign in using an existing account or to register himself with a new account. In the former case
(customer wishes to proceed as guest), the user object remains as it is: Inactive and with an
unusable password. In the second case, the visitor signs in using Django's default authentication
backends. Here the cart's content is merged with the already existing cart of that user object.
In the latter case (customer registers himself), the user object is recycled and becomes an active
Django User object, with a password and an email address.


Authenticating against the Email Address
========================================

Nowadays it is quite common, to use the email address for authenticating, rather than an explicit
account identifier. This in Django is not possible without replacing the built-in User model.
Since for an e-commerce site this authentication variant is rather important, **djangoSHOP** is
shipped with an optional drop-in replacement for the built-in User model.

This convenience User model is almost a copy of the existing ``User`` model as found in
``django.contrib.auth.models.py``, but it uses the field ``email`` rather than ``username`` for
looking up the credentials. To activate it, add to the project's ``settings.py``:

.. code-block:: python

	INSTALLED_APPS = (
	    'django.contrib.auth',
	    'email_auth',
	    ...
	)
	
	AUTH_USER_MODEL = 'email_auth.User'

.. note:: This alternative User model uses the same table as the Django authentication would,
		 namely ``auth_user``. It is even field-compatible with the built-in model and hence can
		 even be used for existing projects.


Caveat when using this alternative User model
--------------------------------------------

The savvy reader may have noticed that in ``email_auth.models.User``, the email field is not
declared as unique. This by the way causes Django to complain during startup with:

.. code-block::

	WARNINGS:
	email_auth.User: (auth.W004) 'User.email' is named as the 'USERNAME_FIELD', but it is not unique.
	    HINT: Ensure that your authentication backend(s) can handle non-unique usernames.

This warning can be silenced by adding ``SILENCED_SYSTEM_CHECKS = ['auth.W004']`` to the project's
``settings.py``.

The reason for this is twofold:

First, Django's default user model has no unique constraint on the email field, so ``email_auth``
remains more compatible.

Second, the uniqueness is only required for users which actually can sign in. Guest users on the
other hand can not sign in, but they may return someday. By having a unique email field, the Django
application ``email_auth`` would lock them out.


Administration of Users and Customers
-------------------------------------

By keeping the Customer- and the User model tight together, it is possible to reuse the Django's
administration backend for both of them. All you have to do is to import and register the
Customer backend inside the project's ``admin.py``:

.. code-block:: python

	from django.contrib import admin
	from shop.admin.customer import CustomerProxy, CustomerAdmin

	admin.site.register(CustomerProxy, CustomerAdmin)


Summary for Customer to User mapping
====================================

This table summarizes to possible mappings between a Django User Model [1]_ and the Shop's Customer
model:

+----------------------------------------+----------------------------------------+----------------+
| Shop's Customer Model                  | Django's User Model                    | Active Session |
+========================================+========================================+================+
| ``VisitingCustomer`` object            | ``AnonymousUser`` object               | No             |
+----------------------------------------+----------------------------------------+----------------+
| Unrecognized ``Customer``              | Inactive User object with unusable     | Yes, but not   |
|                                        | password                               | logged in      |
+----------------------------------------+----------------------------------------+----------------+
| ``Customer`` recognized as guest [2]_  | Inactive User with valid email address | Yes, but not   |
|                                        | but unusable password                  | logged in      |
+----------------------------------------+----------------------------------------+----------------+
| ``Customer`` recognized as guest [3]_  | Active User with valid email address   | Yes, but not   |
|                                        | and unknown, but resetable password    | logged in      |
+----------------------------------------+----------------------------------------+----------------+
| Registered ``Customer``                | Active User with valid email address,  | Yes, logged in |
|                                        | known password, optional salutation,   | using Django's |
|                                        | first- and last names                  | authentication |
|                                        |                                        | backend        |
+----------------------------------------+----------------------------------------+----------------+

.. [1] or any other User model set by ``AUTH_USER_MODEL``.

.. [2] if setting ``SHOP_GUEST_IS_ACTIVE_USER = False`` (the default).

.. [3] if setting ``SHOP_GUEST_IS_ACTIVE_USER = True``.

