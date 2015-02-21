# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView
from shop.models.product import BaseProduct


class ProductViewMixin(object):
    """
    This view handles displaying the products to customers.
    It filters out inactive products.
    """
    model = getattr(BaseProduct, 'MaterializedModel')

    def get_queryset(self):
        return self.model.objects.filter(active=True)


class ProductListView(ProductViewMixin, ListView):
    pass


class ProductDetailView(ProductViewMixin, DetailView):
    pass
