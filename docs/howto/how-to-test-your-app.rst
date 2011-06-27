==============================================
How to test your django-shop based Application
==============================================

Unit testing is an extremely useful bug-killing tool for the modern Web
developer. If you do `TDD
<http://en.wikipedia.org/wiki/Test-driven_development>`_, unit testing is just
mandatory.


Don't use fixtures !
====================

django-shop models are based on polymorphic, which means that a ContentType
reference is added to each Product object.

.. note::

    A reference (ContentType) to the real/leaf model is stored in the base model
    (the base model directly inheriting from PolymorphicModel). You need to be
    aware of this when using the dumpdata management command or any other
    low-level database operations. E.g. if you rename models or apps or copy
    objects from one database to another, then Django's ContentType table needs
    to be corrected/copied too. This is of course generally the case for any
    models using Django's ContentType.

``source``: `django-polymorphic doc
<http://bserve.webhop.org/django_polymorphic/DOCS.html#restrictions-caveats>`_


By doing::

    $ ./manage.py dumpdata yourapp shop polymorphic contenttypes >
        yourapp/fixtures/initial_data.json

You will be able to share the same data between your development installation
and your test server. But you will get troubles with your tests if you use
different databases (eg. mysql for `manage.py runserver` and sqlite3 for
`manage.py test`), because the databases doesn't handle contenttypes the same way.
You'll end up having a reference to a wrong object (like a cart instead of your
product).

Furthermore, if you named your fixtures *initial_data* and didn't specify
another fixture for your test classes, `manage.py test` will load them when
creating the database.


A solution
==========

Runserver
---------

For your regular fixtures, name them *bootstrap* instead of initial_data. Then,
you can do::

    $ ./manage loaddata bootstrap

It will load all your bootstrap.[json|xml|yaml|...] from all your applications.
Consider using `Fabric <http://docs.fabfile.org/>`_ and automatize this task.

By the same way, your `./manage.py syncdb` will become faster and you can choose
when to update your initial data.

Tests
-----

Lots of choices are available for creating your data: raw sql, test fixtures
with correct contentypes, a setup.py script to create your objects, catch the
post_syncdb signal, model object generation.

Here we'll see how to use `Milkman <https://github.com/ccollins/milkman>`_.

Start by adding *milkman* to your requirements.txt file, then::

    $ pip install -r requirements.txt

Then add *milkman* to your test_settings.py `INSTALLED_APPS`.

You can now create a base_test.py file to your tests and create your TestCase
there. Let's use again our example Book model::

    # from django
    from django.contrib.auth.models import User
    from django.test import TestCase

    # from project
    from milkman.dairy import milkman
    from shop.models import Product

    # from app
    from library.models import Book


    class VehicleTestCase(TestCase):
        """Model object generation for our Books"""

        def setUp(self):
            # Simple book
            self.book = milkman.deliver(Book)
            # Book with ForeignKey
            self.bob = milkman.deliver(User)
            self.book_with_author = milkman.deliver(Book,
                author_id = self.bob.id)

If you use Foreignkey in your django-shop inherited model fields, then you
might want to pip from this fork instead::

    $ pip install -e git+https://github.com/Fandekasp/milkman.git#egg=milkman

as the current version doesn't support generation of Objects having foreignkeys.

Be sure to milkman.deliver the ForeignKey dependancy before your object, as
shown in the example above.

.. TODO: Remove this last comment when the pull request from this fork has been
    accepted
