try:
    import redis
except ImportError:
    redis = None
from django.conf import settings
from django.dispatch import Signal


customer_recognized = Signal(providing_args=['customer', 'request'])

if redis and hasattr(settings, 'SESSION_REDIS'):
    redis_con = dict((key, settings.SESSION_REDIS[key]) for key in ['host', 'port', 'db', 'socket_timeout'])
    pool = redis.ConnectionPool(**redis_con)
    redis_con = redis.Redis(connection_pool=pool)
else:
    redis_con = type(str('Redis'), (), {'publish': lambda *args: None})()


def email_queued():
    """
    If SESSION_REDIS is configured, inform a separately running worker engine, that
    emails are ready for delivery. Call this function every time an email has been
    handled over to the Post-Office.
    """
    redis_con.publish('django-SHOP', 'send_queued_mail')
