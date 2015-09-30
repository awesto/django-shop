# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models.address import BaseAddress, ISO_3166_CODES


class Address(BaseAddress):
    addressee = models.CharField(_("Addressee"), max_length=50)
    supplement = models.CharField(_("Supplement"), max_length=50, blank=True, null=True)
    street_name = models.CharField(_("Street name"), max_length=50)
    street_number = models.CharField(_("Number"), max_length=10, blank=False, null=True)
    zip_code = models.CharField(_("ZIP"), max_length=10)
    location = models.CharField(_("Location"), max_length=50)
    country = models.CharField(_("Country"), max_length=3, choices=ISO_3166_CODES, default='DE')
