# -*- coding: utf-8 -*-
'''
This models the checkout process using views.
'''
from django.core.urlresolvers import reverse
from shop.backend_base import backends_pool
from shop.models.ordermodel import Order
from shop.util.cart import get_or_create_cart
from shop.views import ShopTemplateView

class SelectShippingView(ShopTemplateView):
    template_name = 'shop/checkout/choose_shipping.html'
    
    def create_order_object_from_cart(self):
        cart = get_or_create_cart(self.request)
        Order.objects.create_from_cart(cart)
    
    def get_context_data(self, **kwargs):
        ctx = super(SelectShippingView, self).get_context_data(**kwargs)
        shipping_modules_list = backends_pool.get_shipping_backends_list()
        
        self.create_order_object_from_cart()
        
        select = {}
        
        for backend in shipping_modules_list:
            url = reverse(backend.url_namespace)
            select.update({backend.backend_name:url})
        ctx.update({'shipping_options':select})
        return ctx
        
