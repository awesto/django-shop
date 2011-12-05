How to identify a customer
==========================

Introduction
------------
In almost every Internet shop, customers can optionally, or are even required to identify themselves
before proceeding to checkout. In order to do this, they must be identified by the shop, which
itself uses the default mechanisms offered by Django. Thus, an identified customer is stored in the
same database table as the administrators of django-shop, with the exception that they are not
allowed to log into the administrative interface. Moreover a shop customer has to register himself
rather than being added by an administrator.

Installation
------------
The shop must offer its customer an interface to register themselves. Fortunately for us, James
Bennet has written an awesome Django plugin to handle this task.
- From github.com install https://github.com/nathanborror/django-registration.git and move the
directory 'registration' to the path where the other plugins are located.
- In settings.py add to::

    INSTALLED_APPS = (
        ...
        'registration'
        ...
    )

- Since django-registration sends a confirmation E-Mail to the customer, check if your app is
  configured properly. In settings.py, check the values of EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER
  and EMAIL_HOST_PASSWORD. See https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
  for details.
- In urls.py of your shop's application, add to::

    urlpatterns = patterns('',
        ...
        (r'^accounts/', include('registration.backends.default.urls')),
        ...
    )

- In settings.py add::

     LOGIN_REDIRECT_URL = '/shop/'

or to whatever location is appropriate after successful login.

- Unfortunately James Bennet does not offer any default templates for his django-registration
  plugin. You can find sample templates here: https://github.com/yourcelf/django-registration-defaults.git.
  Copy them into your shop's templates directory and adopt them for your needs.

Usage
-----
Somewhere in your shop's templates use::

    {% url auth_login %}

to add a link for customer login and::

    {% url registration_register %}

to  add a link for new customers.
