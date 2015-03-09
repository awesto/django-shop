# -*- coding: utf-8 -*-
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
    priority_shipping = models.SmallIntegerField(default=0,
        help_text=_("Priority of using this address for shipping"))
    priority_invoice = models.SmallIntegerField(default=0,
        help_text=_("Priority of using this address for invoicing"))

    class Meta(object):
        abstract = True
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        ordering = ('priority_shipping', 'priority_invoice')

    def save(self, *args, **kwargs):
        return super(BaseAddress).save(*args, **kwargs)
        # max_priority = self.model.objects.filter().aggregate(max=Max(self.priority_shipping))['max'] or 0

AddressModel = deferred.MaterializedModel(BaseAddress)

