# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from shop.forms import get_cart_item_formset
from shop.models.productmodel import Product
from shop.util.cart import get_or_create_cart
from shop.views import ShopView, ShopTemplateResponseMixin


class CartItemDetail(ShopView):
    """
    A view to handle CartItem-related operations. This is not a real view in
    the sense that it is not designed to answer to GET or POST request nor to
    display anything, but only to be used from AJAX.
    """
    action = None

    def dispatch(self, request, *args, **kwargs):
        """
        Submitting form works only for "GET" and "POST".
        If `action` is defined use it dispatch request to the right method.
        """
        if not self.action:
            return super(CartItemDetail, self).dispatch(request, *args,
                **kwargs)
        if self.action in self.http_method_names:
            handler = getattr(self, self.action, self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Update one of the cartItem's quantities. This requires a single
        ``item_quantity`` POST parameter, but should be posted to a properly
        RESTful URL (that should contain the item's ID):

        http://example.com/shop/cart/item/12345
        """
        cart_object = get_or_create_cart(self.request)
        item_id = self.kwargs.get('id')
        # NOTE: it seems logic to be in POST but as tests client shows
        # with PUT request, data is in GET variable
        # TODO: test in real client
        # quantity = self.request.POST['item_quantity']
        quantity = self.request.POST['item_quantity']
        cart_object.update_quantity(item_id, int(quantity))
        return self.put_success()

    def delete(self, request, *args, **kwargs):
        """
        Deletes one of the cartItems. This should be posted to a properly
        RESTful URL (that should contain the item's ID):

        http://example.com/shop/cart/item/12345
        """
        cart_object = get_or_create_cart(self.request)
        item_id = self.kwargs.get('id')
        cart_object.delete_item(item_id)
        return self.delete_success()

    # success hooks
    def success(self):
        """
        Generic hook by default redirects to cart
        """
        if self.request.is_ajax():
            return HttpResponse('Ok<br />')
        else:
            return HttpResponseRedirect(reverse('cart'))

    def post_success(self, product, cart_item):
        """
        Post success hook
        """
        return self.success()

    def delete_success(self):
        """
        Post delete hook
        """
        return self.success()

    def put_success(self):
        """
        Post put hook
        """
        return self.success()

    # TODO: add failure hooks


class CartDetails(ShopTemplateResponseMixin, CartItemDetail):
    """
    This is the actual "cart" view, that answers to GET and POST requests like
    a normal view (and returns HTML that people can actually see)
    """

    template_name = 'shop/cart.html'
    action = None

    def get_context_data(self, **kwargs):
        # There is no get_context_data on super(), we inherit from the mixin!
        ctx = {}
        state = {}
        cart_object = get_or_create_cart(self.request)
        cart_object.update(state)
        ctx.update({'cart': cart_object})
        ctx.update({'cart_items': cart_object.get_updated_cart_items()})
        return ctx

    def get(self, request, *args, **kwargs):
        """
        This is lifted from the TemplateView - we don't get this behavior since
        this only extends the mixin and not templateview.
        """
        context = self.get_context_data(**kwargs)
        formset = get_cart_item_formset(cart_items=context['cart_items'])
        context.update({'formset': formset, })
        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        """
        This is to *add* a new item to the cart. Optionally, you can pass it a
        quantity parameter to specify how many you wish to add at once
        (defaults to 1)
        """
        product_id = self.request.POST['add_item_id']
        product_quantity = self.request.POST.get('add_item_quantity')
        if not product_quantity:
            product_quantity = 1
        product = Product.objects.get(pk=product_id)
        cart_object = get_or_create_cart(self.request)
        cart_item = cart_object.add_product(product, product_quantity)
        cart_object.save()
        return self.post_success(product, cart_item)

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

        Data should be in update_item_ID=QTY form, where ID is id of cart item
        and QTY is quantity to set.
        """
        context = self.get_context_data(**kwargs)
        formset = get_cart_item_formset(cart_items=context['cart_items'],
                data=self.request.POST)
        if formset.is_valid():
            formset.save()
            return self.put_success()
        context.update({'formset': formset, })
        return self.render_to_response(context)
