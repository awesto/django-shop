# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models import address


class AddressModelMixin(models.Model):
    addressee = models.CharField(_("Addressee"), max_length=50)
    supplement = models.CharField(_("Supplement"), max_length=50, blank=True, null=True)
    street = models.CharField(_("Street"), max_length=50)
    zip_code = models.CharField(_("ZIP"), max_length=10)
    location = models.CharField(_("Location"), max_length=50)
    country = models.CharField(_("Country"), max_length=3, choices=address.ISO_3166_CODES)

    class Meta:
        abstract = True


class ShippingAddress(address.BaseShippingAddress, AddressModelMixin):
    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")


class BillingAddress(address.BaseBillingAddress, AddressModelMixin):
    class Meta:
        verbose_name = _("Billing Address")
        verbose_name_plural = _("Billing Addresses")
