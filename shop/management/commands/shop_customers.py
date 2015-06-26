# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from optparse import make_option
from importlib import import_module
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


class Command(BaseCommand):
    help = _("Collect information about all customers which accessed this shop.")

    option_list = BaseCommand.option_list + (
        make_option("--delete-expired", action='store_true', dest='delete_expired',
            help=_("Delete customers with expired sessions.")),
    )

    def handle(self, verbosity, delete_expired, *args, **options):
        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        Customer = get_user_model()
        data = dict(total=0, anonymous=0, guests=0, registered=0, expired=0)
        for customer in Customer.objects.iterator():
            data['total'] += 1
            if customer.is_anonymous():
                data['anonymous'] += 1
                if customer.session_key and not SessionStore().exists(customer.session_key):
                    data['expired'] += 1
                    if delete_expired:
                        customer.delete()
            elif customer.is_guest():
                data['guests'] += 1
            elif customer.is_registered:
                data['registered'] += 1
        msg = _("Customers in this shop: total={total}, anonymous={anonymous}, expired={expired}, guests={guests}, registered={registered}.")
        self.stdout.write(msg.format(**data))
