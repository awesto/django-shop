# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Holds all the information relevant to the client (addresses for instance)
"""
from six import with_metaclass
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from . import deferred


class BaseAddress(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    priority_shipping = models.SmallIntegerField(null=True, default=None,
        help_text=_("Priority of using this address for shipping"))
    priority_invoice = models.SmallIntegerField(null=True, default=None,
        help_text=_("Priority of using this address for invoicing"))

    class Meta(object):
        abstract = True
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

AddressModel = deferred.MaterializedModel(BaseAddress)
