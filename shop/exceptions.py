# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class ProductNotAvailable(Exception):
    """
    The product being purchased isn't available anymore.
    """
    def __init__(self, product):
        self.product = product
        msg = "Product {} isn't available anymore."
        super(ProductNotAvailable, self).__init__(msg.format(product.product_code))
