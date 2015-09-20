==================
The Customer Model
==================

Most web applications distinguish logged in users explicitly from *the* anonymous site visitor,
which is regarded as a non-existing user, and thus is not referenced a database entity. The Django
framework, in this respect, is no exception.

This pattern is fine for web-sites, which run a Content Management System, a Blog, where only an
elected group of staff users have to authenticate. This approach also works for web-services,
such as social networks or Intranet applications, where the visitors have to authenticate right
from the beginning.

When running an e-commerce site, this use-pattern has serious drawbacks. Normally, a visitor starts
to look for interesting products, hopefully adding a few to his cart. Then on the way to the
checkout, he decides whether to create a user account or continue as guest. Here it get complicated.

First of all, for anonymous users, the cart has to refer against a session entity, rather than
a user object out of the database. Django does not offer a session based anonymous user object, but
each cart must be associated with its site visitor, hence the generic anonymous user object is not
appropriate for this purpose.

Secondly, at the latest when the cart is converted into an order, but the visitor wants to continue
as guest, thus remaining anonymous, that order object must refer to a user object out of the
database. These kind of users would be regarded as fakes, unable to log in, reset their password,
etc. The only information which must be stored for such a faked user, is its email address.
otherwise she couldn't be informed, whenever the state of its order changed.

Django does not explicitly allow such users in its database models. By using the boolean flag
``is_active``, or by setting the password to be unusable, we can fool an application to interpret
such a user as a faked anonymous user, but this approach is unportable across all Django based
applications using the authentication system.

Therefore djangoSHOP introduces a new database model – the ``Customer`` model.


Properties of the Customer Model
================================

The ``Customer`` model is an extension to the existing ``User`` model. It has a 1:1 relation, and
for each customer, there always exists a user object. This approach allows us to do a few things:

The built-in User object can be swapped out and replaced against another implementation. Such an
alternative implementation has a small limitation. It must inherit from
``django.contrib.auth.models.AbstractBaseUser`` and define the all the fields, which also are
available in the default User model.

We can create faked users in the database, tagging them as anonymous users. This has another
advantage. By storing the session key of the site visitor inside the User object, it is possible to
establish a connection between a User object in the database with an otherwise anonymous visitor.
This further allows the Cart and the Order models always refer to the User model, since they don't 
have to care about whether this user authenticated or not. It also keeps the workflow simple,
whenever an anonymous users decides to register and authenticate himself.


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

