import os
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
try:
    import uwsgidecorators

    @uwsgidecorators.timer(15)
    def send_queued_mail(num):
        """
        Send queued mail every 15 seconds
        """
        call_command('send_queued_mail')

    @uwsgidecorators.cron(0, 6, -1, -1, -1)
    def rebuild_index(num):
        """
        Rebuild search index in the morning
        """
        call_command('rebuild_index', interactive=False)

    @uwsgidecorators.cron(30, 5, -1, -1, 0)
    def shopcustomers(num):
        """
        Delete expired customers every Sunday
        """
        call_command('shopcustomers', delete_expired=True)

except ImportError:
    print("uwsgidecorators not found. Cron and timers are disabled")

application = get_wsgi_application()

# rebuild full text search index on first bootstrap
BOOTSTRAP_FILE = os.path.join(os.getenv('DJANGO_WORKDIR', ''), '.bootstrap')
if os.path.isfile(BOOTSTRAP_FILE):
    call_command('initialize_shop_demo', interactive=False)
    call_command('rebuild_index', interactive=False)
    os.remove(BOOTSTRAP_FILE)
