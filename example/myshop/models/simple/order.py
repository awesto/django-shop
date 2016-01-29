# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models.order import BaseOrderItem


class OrderItem(BaseOrderItem):
    quantity = models.IntegerField(_("Ordered quantity"))
