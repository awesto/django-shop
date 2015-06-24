# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from importlib import import_module
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


class Command(BaseCommand):
    help = _("Remove anonymous customers with expired sessions")

    def handle(self, *args, **options):
        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        Customer = get_user_model()
        count = 0
        for customer in Customer.objects.iterator():
            if customer.session_key and customer.is_anonymous():
                if not SessionStore().exists(customer.session_key):
                    count += 1
                    customer.delete()
        print("Removed {0} anonymous customers from shop".format(count))
