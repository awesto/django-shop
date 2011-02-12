# -*- coding: utf-8 -*-
from shop.views import ShopTemplateView
from shop.util.cart import get_or_create_cart

class CartDetails(ShopTemplateView):
    template_name = 'shop/cart_detail.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(CartDetails,self).get_context_data(**kwargs)
        cart_object = get_or_create_cart(self.request)
        ctx.update({'cart': cart_object})
        return ctx

    