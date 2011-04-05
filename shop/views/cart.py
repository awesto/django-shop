# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from shop.models.cartmodel import CartItem
from shop.models.productmodel import Product
from shop.util.cart import get_or_create_cart
from shop.views import ShopTemplateView, ShopView

class CartItemDetail(ShopView):
    '''
    A view to handle CartItem-related operations. This is not a real view in the
    sense that it is not designed to answer to GET or POST request nor to display
    anything, but only to be used from AJAX.
    '''
    action = None
    
    def dispatch(self, request, *args, **kwargs):
        """
        Submitting form works only for "GET" and "POST".
        If `action` is defined use it dispatch request to the right method.
        """
        if not self.action:
            return super(CartDetails, self).dispatch(request, *args, **kwargs)
        if self.action in self.http_method_names:
            handler = getattr(self, self.action, self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(request, *args, **kwargs)
    
    def put(self):
        '''
        Update one of the cartItem's quantities. This requires a single 'item_quantity'
        POST parameter, but should be posted to a properly RESTful URL (that should
        contain the item's ID):
        
        http://example.com/shop/cart/item/12345
        '''
        cart_object = get_or_create_cart(self.request)
        item_id = self.kwargs.get('id')
        quantity = self.request.POST['item_quantity']
        cart_object.update_quantity(item_id, int(quantity))
        # TODO: Finish by returning something
    
    def delete(self):
        '''
        Deletes one of the cartItems. This should be posted to a properly 
        RESTful URL (that should contain the item's ID):
        
        http://example.com/shop/cart/item/12345
        '''
        cart_object = get_or_create_cart(self.request)
        item_id = self.kwargs.get('id')
        cart_object.delete_item(item_id)
        # TODO: Finish by returning something
    
    # success hooks
    def success(self):
        """
        Generic hook by default redirects to cart
        """
        if self.request.is_ajax():
            return HttpResponse('Ok<br />')
        else:
            return HttpResponseRedirect(reverse('cart'))

    def post_success(self, item):
        """
        Post success hook"
        """
        return self.success()

    def delete_success(self):
        """
        Post delete hook"
        """
        return self.success()

    def put_success(self):
        """
        Post put hook"
        """
        return self.success()

    # TODO: add failure hooks

class CartDetails(ShopTemplateView, CartItemDetail):
    '''
    This is the actual "cart" view, that answers to GET and POST requests like
    a normal view (and returns HTML that people can actually see)
    '''
    
    template_name = 'shop/cart.html'
    action = None

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
        This is to *add* a new item to the cart, therefore the quantity is 
        irrelevant (it should always be 1)
        '''
        item_id = self.request.POST['add_item_id']

        item = Product.objects.get(pk=item_id)
        cart_object = get_or_create_cart(self.request)
        cart_object.add_product(item)
        cart_object.save()
        return self.post_success(item)

    def delete(self, *args, **kwargs):
        """
        Empty shopping cart.
        """
        cart_object = get_or_create_cart(self.request)
        cart_object.empty()
        return self.delete_success()

    def put(self, *args, **kwargs):
        """
        Update shopping cart items quantities.

        Data should be in update_item-ID=QTY form, where ID is id of cart item
        and QTY is quantity to set.
        """
        field_prefix = 'update_item-'
        cart_item_fields = [k for k in self.request.POST.keys() 
                if k.startswith(field_prefix)]
        cart_object = get_or_create_cart(self.request)
        for key in cart_item_fields:
            id = key[len(field_prefix):]
            cart_object.update_quantity(id, int(self.request.POST[key]))
        return self.put_success()
