#!/usr/bin/env python
import redis
import schedule
import time


if __name__ == '__main__':
    from django import setup
    from django.conf import settings
    from django.core.management import call_command
    from django.utils import timezone

    # initialize Django
    setup()

    # schedule jobs
    schedule.every().minute.do(call_command, 'send_queued_mail')
    rebuild_at = timezone.now() + timezone.timedelta(minutes=6)
    schedule.every().hour.at(rebuild_at.strftime('*:%M')).do(call_command, 'rebuild_index', interactive=False)
    schedule.every().sunday.do(call_command, 'shopcustomers', delete_expired=True)

    if hasattr(settings, 'SESSION_REDIS'):
        redis_con = dict((key, settings.SESSION_REDIS[key]) for key in ['host', 'port', 'db', 'socket_timeout'])
        pool = redis.ConnectionPool(**redis_con)
        r = redis.Redis(connection_pool=pool)
        pubsub = r.pubsub()
        pubsub.subscribe('django-SHOP')
    else:
        pubsub = type('PubSub', (), {'get_message': lambda s: None})()

    while True:
        message = pubsub.get_message()
        if message:
            if message['data'] == 'send_queued_mail':
                call_command('send_queued_mail')
        schedule.run_pending()
        time.sleep(1)
