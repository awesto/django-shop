# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Holds all the information relevant to the client (addresses for instance)
"""
from six import with_metaclass
from django.conf import settings
from django.db import models
from django.template.loader import select_template, Context
from django.utils.translation import ugettext_lazy as _
from shop import settings as shop_settings
from . import deferred


class BaseAddress(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    customer = deferred.ForeignKey('BaseCustomer')
    priority_shipping = models.SmallIntegerField(null=True, default=None,
        help_text=_("Priority of using this address for shipping"))
    priority_billing = models.SmallIntegerField(null=True, default=None,
        help_text=_("Priority of using this address for invoicing"))

    class Meta(object):
        abstract = True
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def as_text(self):
        """
        Return the address as plain text to be used for printing, etc.
        """
        template_names = [
            '{}/address.txt'.format(shop_settings.APP_LABEL),
            'shop/address.txt',
        ]
        template = select_template(template_names)
        context = Context({'address': self})
        return template.render(context)

AddressModel = deferred.MaterializedModel(BaseAddress)

ISO_3166_CODES = (
    ('AT', _("Austria")),
    ('DE', _("Germany")),
    ('DK', _("Denmark")),
    ('CH', _("Switzerland")),
    ('NL', _("Nederlands")),
)
