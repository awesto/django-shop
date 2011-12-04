# -*- coding: utf-8 -*-
from shop.models.productmodel import Product
from shop.views import ShopDetailView


class ProductDetailView(ShopDetailView):
    """
    This view handles displaying the right template for the subclasses of
    Product.
    It will look for a template at the normal (conventional) place, but will
    fallback to using the default product template in case no template is
    found for the subclass.
    """
    model = Product  # It must be the biggest ancestor of the inheritence tree.
    generic_template = 'shop/product_detail.html'

    def get_template_names(self):
        ret = super(ProductDetailView, self).get_template_names()
        if not self.generic_template in ret:
            ret.append(self.generic_template)
        return ret
