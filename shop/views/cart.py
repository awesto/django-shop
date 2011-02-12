# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from shop.models.cartmodel import Cart
from shop.views import ShopTemplateView

class CartDetails(ShopTemplateView):
    template_name = 'shop/cart_detail.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(CartDetails,self).get_context_data(**kwargs)
        if not isinstance(self.request.user,AnonymousUser):
            cart_object = Cart.objects.filter(user=self.request.user)
            if not cart_object:
                cart_object = Cart.objects.create(user=self.request.user)
        else:
            cart_object = None
        ctx.update({'cart': cart_object})
        return ctx

    