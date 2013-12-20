# -*- coding: utf-8 -*-
from shop.models.productmodel import Product
from shop.views import (ShopListView, ShopDetailView)


class ProductListView(ShopListView):
    """
    This view handles displaying the product catalogue to customers.
    It filters out inactive products and shows only those that are active.
    """
    generic_template = 'shop/product_list.html'

    def get_queryset(self):
        """
        Return all active products.
        """
        return Product.objects.filter(active=True)


class ProductDetailView(ShopDetailView):
    """
    This view handles displaying the right template for the subclasses of
    Product.
    It will look for a template at the normal (conventional) place, but will
    fallback to using the default product template in case no template is
    found for the subclass.
    """
    model = Product  # It must be the biggest ancestor of the inheritance tree.
    generic_template = 'shop/product_detail.html'

    def get_template_names(self):
        ret = super(ProductDetailView, self).get_template_names()
        if not self.generic_template in ret:
            ret.append(self.generic_template)
        return ret

