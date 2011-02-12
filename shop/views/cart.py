# -*- coding: utf-8 -*-
from shop.models.cartmodel import CartItem
from shop.models.productmodel import Product
from shop.util.cart import get_or_create_cart
from shop.views import ShopTemplateView
from django.http import HttpResponse

class CartDetails(ShopTemplateView):
    template_name = 'shop/cart.html'
    add_to_cart_redirect = HttpResponse('Ok<br />')
    
    def get_context_data(self, **kwargs):
        ctx = super(CartDetails,self).get_context_data(**kwargs)
        
        cart_object = get_or_create_cart(self.request)
        cart_object.update()
        ctx.update({'cart': cart_object})
        
        cart_items = CartItem.objects.filter(cart=cart_object)
        final_items = []
        for item in cart_items:
            item.update()
            final_items.append(item)
        ctx.update({'cart_items': final_items})
        
        return ctx
    
    def post(self, *args, **kwargs):
        '''
        We expect to be posted with add_item_id and add_item_quantity set in
        the POST 
        '''
        item_id = self.request.POST['add_item_id']
        quantity = self.request.POST['add_item_quantity']
        
        item = Product.objects.get(pk=item_id)
        cart_object = get_or_create_cart(self.request)
        cart_object.add_product(item, quantity)
        cart_object.save()
        return self.add_to_cart_redirect
    