# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from shop.models.cartmodel import Cart
from shop.views import ShopTemplateView

class CartDetails(ShopTemplateView):
    template_name = 'shop/cart/cart_detail.html'
    
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

#def add_product_to_cart(request, product_id):
#    '''
#    Adds a product passed in parameter (via its ID) to the current user's 
#    shopping basket.
#    '''
#    shopping_cart_id = request.user.get('shopping_cart', False)
#    if not shopping_cart_id:
#        shopping_cart_id = request.session.get('shopping_cart', False)
#    if not shopping_cart_id:
#        #TODO Handle the no user + no session case
#        pass
#    
#    shopping_cart = Cart.objects.get(pk=shopping_cart_id)
#    product = Product.objects.get(pk=product_id)
#    shopping_cart.add_product(product)
#    #TODO: Class based views. Really.
    