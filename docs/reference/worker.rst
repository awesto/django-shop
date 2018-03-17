.. _reference/worker:

=============================
Working off Asynchronous Jobs
=============================

A merchant implementation serving **django-SHOP**, usually runs a few asynchronous jobs, such as
cleaning stale entries, sending e-mail and building the search index. In Django, there are many
ways to handle this, usually by integrating `Celery into Django`_. However, a Celery setup is
unnecessarily complicated and usually not required. Instead we can handle all of our asynchronous
jobs using a short Python script, referred to as "The Worker" in the documentation. This
stand-alone program runs in the same environment as our Django app.

Here is a short example, which can be used as a blueprint for your own implementation:

.. code-block:: python
	:caption: worker.py

	#!/usr/bin/env python
	import os
	import redis
	import schedule
	import time

	if __name__ == '__main__':
	    from django import setup
	    from django.conf import settings
	    from django.core.management import call_command

	    # initialize Django
	    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_shop.settings')
	    setup()

	    # schedule jobs
	    schedule.every().sunday.do(call_command, 'shopcustomers', delete_expired=True)
	    schedule.every().day.at('10:00').do(call_command, 'rebuild_index', interactive=False)
	    schedule.every().minute.do(call_command, 'send_queued_mail')

	    if hasattr(settings, 'SESSION_REDIS'):
	        redis_con = dict((key, settings.SESSION_REDIS[key]) for key in ['host', 'port', 'db', 'socket_timeout'])
	        pool = redis.ConnectionPool(**redis_con)
	        r = redis.Redis(connection_pool=pool)
	        pubsub = r.pubsub()
	        pubsub.subscribe('django-SHOP')
	    else:
	        # we don't have a Redis message queue, emulate `pubsub`
	        pubsub = type(str('PubSub'), (), {'get_message': lambda s, timeout=1: time.sleep(timeout)})()

	    while True:  # the main loop
	        message = pubsub.get_message(timeout=60)
	        if message and message['data'] == 'send_queued_mail':
	            call_command('send_queued_mail')
	        schedule.run_pending()

Here we schedule three jobs:

* Once a week we remove customers, whose session expired and which never made it to the checkout.
* Once a day we rebuild the search index for the Elasticsearch database.
* At least once a minute we send emails pending in the queue. If Redis is configured, **django-SHOP**
  uses its internal message broker, and whenever an email is added to the queue, the asynchronous
  worker is notified, in order to send it straightaway.

.. _Celery into Django: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
