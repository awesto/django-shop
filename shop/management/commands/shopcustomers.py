# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _


class Command(BaseCommand):
    help = _("Collect information about all customers which accessed this shop.")

    def add_arguments(self, parser):
        parser.add_argument("--delete-expired", action='store_true', dest='delete_expired',
            help=_("Delete customers with expired sessions."))

    def handle(self, verbosity, delete_expired, *args, **options):
        from shop.models.customer import CustomerModel
        data = dict(total=0, anonymous=0, active=0, staff=0, guests=0, registered=0, expired=0)
        for customer in CustomerModel.objects.iterator():
            data['total'] += 1
            if customer.user.is_active:
                data['active'] += 1
            if customer.user.is_staff:
                data['staff'] += 1
            if customer.is_registered():
                data['registered'] += 1
            elif customer.is_guest():
                data['guests'] += 1
            elif customer.is_anonymous():
                data['anonymous'] += 1
            if customer.is_expired():
                data['expired'] += 1
                if delete_expired:
                    customer.delete()
        msg = _("Customers in this shop: total={total}, anonymous={anonymous}, expired={expired}, active={active}, guests={guests}, registered={registered}, staff={staff}.")
        self.stdout.write(msg.format(**data))
