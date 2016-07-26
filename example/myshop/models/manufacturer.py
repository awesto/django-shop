# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Manufacturer(models.Model):
    name = models.CharField(_("Name"), max_length=50)

    def __str__(self):
        return self.name
