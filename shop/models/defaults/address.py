# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models import address

COUNTRY_CODES = (
    ('AT', _("Austria")),
    ('DE', _("Germany")),
    ('DK', _("Denmark")),
    ('CH', _("Switzerland")),
    ('NL', _("Nederlands")),
)


class Address(address.BaseAddress):
    """
    Default materialized model for Address.
    """
    addressee = models.CharField(max_length=50, verbose_name=_("Addressee"))
    supplement = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Supplement"))
    street = models.CharField(max_length=50, verbose_name=_("Street"))
    zip_code = models.CharField(max_length=10, verbose_name=_("ZIP Code"))
    location = models.CharField(max_length=50, verbose_name=_("Location"))
    country = models.CharField(max_length=3, choices=COUNTRY_CODES)
