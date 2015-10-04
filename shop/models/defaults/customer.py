# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models.customer import BaseCustomer


class Customer(BaseCustomer):
    """Default materialized model for Customer"""

    number = models.PositiveIntegerField(_("Customer Number"), null=True, default=None, unique=True)

    def get_or_assign_number(self):
        """
        Assign a number to be used as unique customer identifier.
        """
        if self.number is None:
            number = Customer.objects.filter(number__isnull=False).aggregate(models.Max('number'))
            self.number = number + 1
            self.save()
        return self.number
