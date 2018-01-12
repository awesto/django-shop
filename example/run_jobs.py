from django.core.management import call_command

"""
Work in progress. Use this for scheduling jobs.
"""

# every 15 seconds
def send_queued_mail(num):
    """
    Send queued mail every 15 seconds
    """
    call_command('send_queued_mail')

# once an hour
def rebuild_index(num):
    """
    Rebuild search index
    """
    call_command('rebuild_index', interactive=False)

# every Sunday night
def shopcustomers(num):
    """
    Delete expired customers every Sunday
    """
    call_command('shopcustomers', delete_expired=True)
