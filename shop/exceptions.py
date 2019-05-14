# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _


class ProductNotAvailable(Exception):
    """
    The product being purchased isn't available anymore.
    """
    def __init__(self, product):
        msg = _("Product {} isn't available anymore.")
        super(ProductNotAvailable, self).__init__(msg.format(product.product_code))
