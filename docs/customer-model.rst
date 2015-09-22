==================
The Customer Model
==================

Most web applications distinguish logged in users explicitly from *the* anonymous site visitor,
which is regarded as a non-existing user, and thus is not referenced by a database entity. The
Django framework, in this respect, is no exception.

This pattern is fine for web-sites, which run a Content Management System, a Blog, where only an
elected group of staff users shall be permitted to access. This approach also works for web-services,
such as social networks or Intranet applications, where the visitors have to authenticate right
from the beginning.

When running an e-commerce site, this use-pattern has serious drawbacks. Normally, a visitor starts
to look for interesting products, hopefully adding a few to his cart. Then on the way to the
checkout, he decides whether to create a user account, use an existing one or continue as guest.
Here things get complicated.

First of all, for non authenticated site visitors, the cart does not belong to anybody. But each
cart must be associated with its site visitor, hence the generic anonymous user object is not
appropriate for this purpose. Unfortunately the Django framework does not offer a session based
anonymous user object.

Secondly, at the latest when the cart is converted into an order, but the visitor wants to continue
as guest, thus remaining anonymous, that order object must refer to a user object in the database.
These kind of users would be regarded as fakes, unable to log in, reset their password, etc. The
only information which must be stored for such a faked user, is her email address otherwise she
couldn't be informed, whenever the state of her order changed.

Django does not explicitly allow such users in its database models. By using the boolean flag
``is_active``, or by setting the password to be unusable, we can fool an application to interpret
such a user as a faked anonymous user, but this approach is unportable across all Django based
applications using the authentication system.

Therefore djangoSHOP introduces a new database model – the ``Customer`` model, which extends the
existing ``User`` model.


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

We can create faked users in the database, tagging them as anonymous users. This has another
advantage. By storing the session key of the site visitor inside the User object, it is possible to
establish a connection between a User object in the database with an otherwise anonymous visitor.
This further allows the Cart and the Order models always refer to the User model, since they don't 
have to care about whether this user authenticated or not. It also keeps the workflow simple,
whenever an anonymous users decides to register and authenticate himself.


Add the Customer model to your application
------------------------------------------

As almost all models in ***djangoSHOP*, the Customer itself is deferrable_. This means that
the merchant has to materialize that model, whereby he can add arbitrary fields to the model.

The simplest way is to materialize the given convenience class in the applications ``models.py``:

.. code-block:: python

	from shop.models.defaults.customer import Customer

or, if you needs extra fields, then instead of the above, do:

.. code-block:: python

	from shop.models.customer import BaseCustomer

	class (BaseCustomer):
	    birth_date = models.DateField("Date of Birth")
	    # other customer related fields

Customers are created automatically with each unique visitor accessing the site. This is done in the
djangoSHOP's customer middleware, which must be added to the ``settings.py`` of your application:

.. code-block:: python

	MIDDLEWARE_CLASSES = (
	    ...
	    'django.contrib.auth.middleware.AuthenticationMiddleware',
        'shop.middleware.CustomerMiddleware',
	    ...
	)

Additionally, some templates may need to access the customer object through the ``RequestContext``.
Therefore, in the ``settings.py`` of your application, add this context processor:

.. code-block:: python

	TEMPLATE_CONTEXT_PROCESSORS = (
	    ...
	    'shop.context_processors.customer',
	    ...
	)

.. _deferrable: deferred-models


Implementation Details
----------------------

The Customer model has a non-nullable one-to-one relation to the User model. Therefore, each
Customer is associated with exactly one one User. For instance, accessing the hashed password can
be achieved through ``customer.user.password``. Some common fields and methods from the User model,
such as ``first_name``, ``last_name``, ``email``, ``is_anonymous()`` and ``is_authenticated()`` are
accessible directly, when working with a customer object. Saving an instance of type Customer, also
invokes method ``save()`` from the associated User model.

The other direction – accessing the Customer model from a User – does not always work. Accessing
an attribute that way, fails if the corresponding Customer is missing.

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


Authenticating against the Email Address
----------------------------------------

Nowadays it is quite common, to use the email address for authenticating, rather than an explicit
account identifier. This in Django is not possible without replacing the built-in User model.
For an e-commerce site this authentication variant is rather important, therefore **djangoSHOP**
is shipped with an optional replacement for the built-in User model.

This convenience User model is almost a copy of the existing ``User`` model as found in
``django.contrib.auth.models.py``, but it uses the field ``email`` rather than ``username`` for
looking up the credentials.

You may optionally use it by importing the alternative implementation into ``models.py`` of your
application:

.. code-block:: python

	from shop.models.defaults.auth import User

and then using that model in your ``settings.py``: 

	AUTH_USER_MODEL = 'my_application.User'


Administration of Users and Customers
-------------------------------------

By keeping the Customer- and the User model tight together, it is possible to share Django's
backend interface for both of them. All you have to do is to import and register the administration
classes into ``admin.py`` of your application:

.. code-block:: python

	from django.contrib import admin
	from django.contrib.auth import get_user_model
	from shop.admin.customer import CustomerAdmin

	admin.site.register(get_user_model(), CustomerAdmin)

The 
