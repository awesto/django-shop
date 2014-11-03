import django

from django.db import transaction

if django.VERSION >= (1, 6):
    atomic = transaction.atomic
else:
    atomic = transaction.commit_on_success
