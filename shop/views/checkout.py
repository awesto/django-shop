# -*- coding: utf-8 -*-
'''
This models the checkout process using views.
'''
from shop.backend_base import backends_pool
from shop.views import ShopTemplateView

class SelectShippingView(ShopTemplateView):
    template_name = 'shop/choose_shipping.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(SelectShippingView, self).get_context_data(**kwargs)
        shipping_modules_list = backends_pool.get_shipping_backends_list()
        
        select = {}
        
        for backend in shipping_modules_list:
            #make a name:namespace dictionnary
            select.update({backend.backend_name:backend.url_namespace})
        ctx.update({'shipping_options':select})
        return ctx
        
