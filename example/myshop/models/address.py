# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models.address import BaseAddress, ISO_3166_CODES


class Address(BaseAddress):
    addressee = models.CharField(max_length=50, verbose_name=_("Addressee"))
    supplement = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Supplement"))
    street_name = models.CharField(max_length=50, verbose_name=_("Street name"))
    street_number = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("Number"))
    zip_code = models.CharField(max_length=10, verbose_name=_("ZIP"))
    location = models.CharField(max_length=50, verbose_name=_("Location"))
    country = models.CharField(max_length=3, choices=ISO_3166_CODES)
