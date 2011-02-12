# -*- coding: utf-8 -*-
from shop.models.productmodel import Product, Category
from shop.views import ShopDetailView

class CategoryDetailView(ShopDetailView):
    '''
    This is the detail view for a category.
    It add the category as 'object' to the context, and the list of products
    belonging to this category as 'product_list'
    '''
    model=Category # Makes no sense for other models
    
    def get_context_data(self, **kwargs):
        ctx = super(CategoryDetailView, self).get_context_data(**kwargs)
        product_list = Product.objects.active().filter(category=self.object)
        ctx.update({'product_list':product_list})
        return ctx