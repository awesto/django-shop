# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from shop.models.address import BaseShippingAddress, BaseBillingAddress, CountryField


class AddressModelMixin(models.Model):
    name = models.CharField(
        _("Full name"),
        max_length=1024,
    )

    address1 = models.CharField(
        _("Address line 1"),
        max_length=1024,
    )

    address2 = models.CharField(
        _("Address line 2"),
        max_length=1024,
        blank=True,
        null=True,
    )

    zip_code = models.CharField(
        _("ZIP / Postal code"),
        max_length=12,
    )

    city = models.CharField(
        _("City"),
        max_length=1024,
    )

    country = CountryField(_("Country"))

    class Meta:
        abstract = True


class ShippingAddress(BaseShippingAddress, AddressModelMixin):
    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")


class BillingAddress(BaseBillingAddress, AddressModelMixin):
    class Meta:
        verbose_name = _("Billing Address")
        verbose_name_plural = _("Billing Addresses")
