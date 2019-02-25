==========================
HTML Email Template Engine
==========================

This is a modified Django Template Engine, which is able to render HTML emails with embedded
inline images.

It requires a version of `Django Post-Office`_ which supports inline attachments. Currently not
even the latest version (3.1) offers this feature. Therefore please use my patched version from
GitHub: https://github.com/jrief/django-post_office/archive/attachments-allowing-MIMEBase.zip

.. _Django Post-Office: https://pypi.org/project/django-post_office/


Installation
============

Change the project's ``settings.py`` to

.. code-block:: python

	INSTALLED_APPS = [
	    …
	    'html_email',
	    …
	]

and

.. code-block:: python

	TEMPLATES = [
	    {
	        …
	    }, {
	        'BACKEND': 'html_email.template.backends.html_email.EmailTemplates',
	        'APP_DIRS': True,
	        'DIRS': [],
	        'OPTIONS': {
	            'context_processors': [
	                'django.contrib.auth.context_processors.auth',
	                'django.template.context_processors.debug',
	                'django.template.context_processors.i18n',
	                'django.template.context_processors.media',
	                'django.template.context_processors.static',
	                'django.template.context_processors.tz',
	                'django.template.context_processors.request',
	            ]
	        }
	    }
	]


Usage
=====

In templates used to render HTML for emails add

.. code-block:: Django

	{% load … html_email %}

This adds one extra templatetag named ``image_src`` which takes one parameter. This can either be
the path to an image file, or a file object itself. Templates rendered using this templatetag,
render a reference ID for each given image, and keep track of those images. Later on, when the
rendered template is passed to the mailing library, those images are attached as ``MIMEImage``s to
the mail's body.

To send an email containing both, a plain text body and some HTML with inlined images, use the
following code snippet:

.. code-block:: python

	from django.core.mail import EmailMultiAlternatives

	subject, body, from_email, to_email = "Hello", "Plain text body", "no-reply@mysite.com", "john@example.com"
	context = {…}
	email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
	template = get_template('email-template-name.html', using='html_email')
	html = template.render(context)
	email_message.attach_alternative(html, 'text/html')
	email_message.mixed_subtype = 'related'
	template.attach_images(email_message)
	email_message.send()
