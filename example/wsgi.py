from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
try:
    import uwsgidecorators
except ImportError:
    uwsgidecorators = None

application = get_wsgi_application()
call_command('rebuild_index', interactive=False)

if uwsgidecorators:
    @uwsgidecorators.timer(15)
    def send_queued_mail(num):
        call_command('send_queued_mail')

    @uwsgidecorators.cron(0, 6, -1, -1, -1)
    def rebuild_index(num):
        call_command('rebuild_index', interactive=False)

    @uwsgidecorators.cron(30, 5, -1, -1, 0)
    def shopcustomers(num):
        call_command('shopcustomers', delete_expired=True)
