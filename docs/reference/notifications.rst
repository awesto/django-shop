.. _reference/notifications:

=============
Notifications
=============

Whenever the status in model ``Order`` changes, the built-in Finite State Machine emits a signal
using Django's `signaling framework`_. These signals are received by **django-SHOP**'s Notification
Framework.


Notification Admin
==================

In Django's admin backend on **Start > Shop > Notification**, the merchant can configure which
email to send to whom, depending on each of the emitted events. When adding or editing a
notification, we get a form mask with four input fields:


Notification Identifier
-----------------------

An arbitrary name used to distinguish the different notifications. It's up to the merchant to choose
a meaningful name, "Order confirmed, paid with PayPal" could for instance be a good choice.


Event Type
----------

Each :ref:`reference/order-workflows` declares a set of transition targets. For instance, the class
``PayInAdvanceWorkflowMixin`` declares these targets: "*Awaiting a forward fund payment*",
"*Prepayment deposited*" and "*No Payment Required*".

The merchant can attach a notification for each of these transition targets. Here he must
choose one from the prepared collection.


The Recipient
-------------

Transitions events are transmitted for changes in the order status. Each order belongs to one
customer, and normally he's the first one to be informed, if something changes.

But other persons in the context of this e-commerce site might also be interested into a
notification. In **django-SHOP** all staff Users qualify, as it is assumed that they belong to the
group eligible to manage the site.


Email Templates
---------------

From the section **Start > Post Office > Email Templates**, choose on of the
:ref:`reference/post-office-emails`.


Notification attachments
------------------------

Choose none, one or more static files to be attached to each email. This typically is a PDF with
the terms and conditions. We normally want to send them only to our customers, but not to the
staff users, otherwise we'd fill up their mail inbox with countless attachments.


Post Office
===========

Emails for order confirmations are send asynchronously by **django-SHOP**. The reason for this is
that it sometimes takes a few seconds for an application server to connect via SMTP, and deliver
an Email. It is unacceptable to do this synchronously during the most sensitive phase of a purchase
operation.

Therefore **django-SHOP** sends all generated emails using the queuing mail system `Post Office`_.
This app can hold a set of different email templates, which use the same template language as Django
itself. Emails can be rendered using plain text, HTML or both.

When emails are queued, the chosen template object is stored side by side with its context
serialized as JSON. These queued emails are accessible in Django's admin backend at
**Start > Post Office > Emails**. Their status can either be "*queued*", "*sent*" or "*failed*".

As an offline operation, ``./manage.py send_queued_mail`` renders and sends queued emails to the
given recipient. During this step, the given template is rendered applying the stored context.
Their status then changes to "*sent*", or in case of a problem to "*failed*".

If **django-SHOP** is configured to run in a multilingual environment, post office renders the email
in the language used during order creation.


.. _reference/post-office-emails:

Templates for Emails
--------------------

The **Message** fields can contain any code, which is valid for Django templates. Frequently, a
summary of the order is rendered in these emails, creating a list of ordered items. This list often
is common across all email templates, and therefore it is recommended to prepare it in a base
template for being reused. In the merchants project folder, create those base email templates
inside the folder ``templates/myshop/email/...``. Then inside the **Message** fields, these
templates can be loaded and expanded using the well known templatetag

.. code-block:: django

	{% extends "myshop/email/somebase.html" %}


Caveats when using an HTML Message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Displaying HTML in email clients is a pain. Nobody really can say, which HTML tags are allowed
in which client – and there are many email readers out there, far more than Internet browsers.

Therefore when designing HTML templates for emails, one must be really, really conservative.
It may seem anachronistic, but still a best practice is to use the ``<table>`` element, and if
necessary, nest it into their ``<td>`` (tables data) elements. Moreover, use inline styles rather
than a ``<style>`` element containing blocks of CSS. It is recommended to use a special
`email framework`_ to avoid nasty quirks, when rendering the templates.

Images can be embedded into HTML emails using two different methods. One is to host the image on the
web-server and to build an absolute URI referring it. Therefore **django-SHOP** enriches the object
``RenderContext`` with the base URI for that web-site and stores it as context variable named
``ABSOLUTE_BASE_URI``. For privacy reasons, most email clients do not load externally hosted images
by default – the customer then must actively request to load them from the external sources.

Another method for adding images to HTML emails is to inline their payload. This means that images,
instead of referring them by URI, are inlined as a base64-encoded string. Easy-thumbnails_ offers a
template filter named ``data_uri`` to perform this operation. This of course blows up the overall
size of an email and shall only be used for small an medium sized images.


.. _signaling framework: https://docs.djangoproject.com/en/stable/topics/signals/
.. _Post Office: https://github.com/ui/django-post_office
.. _Easy-thumbnails: http://easy-thumbnails.readthedocs.org/en/latest/usage/#easy_thumbnails.templatetags.thumbnail.data_uri
.. _email framework: http://emailframe.work/
