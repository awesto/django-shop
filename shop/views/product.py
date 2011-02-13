# -*- coding: utf-8 -*-
from shop.models.productmodel import Product
from shop.views import ShopDetailView

class ProductDetailView(ShopDetailView):
    '''
    This view handles displaying the right template for the subclasses of 
    Product.
    It will look for a template at the normal (conventional) place, but will
    fallback to using the default product template in case no template is
    found for the subclass.
    
    Yes, it's magic. :)
    '''
    model=Product # It must be the biggest ancestor of the inheritence tree.
    
    def get_object(self, queryset=None):
        obj = super(ProductDetailView,self).get_object(queryset)
        return obj.specify()

    def get_template_names(self):
        ret = super(ProductDetailView, self).get_template_names()
        ret.append('shop/product_detail.html')
        return ret