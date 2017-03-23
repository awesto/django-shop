from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

try:
    from datetime import datetime, timedelta
    import uwsgidecorators

    @uwsgidecorators.timer(15)
    def send_queued_mail(num):
        """
        Send queued mail every 15 seconds
        """
        call_command('send_queued_mail')

    trigger_at = datetime.now() + timedelta(minutes=10)
    @uwsgidecorators.cron(trigger_at.minute, -1, -1, -1, -1)
    def rebuild_index(num):
        """
        Rebuild search index
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
