# -*- coding: utf-8 -*-
"""
This models the checkout process using views.
"""
from django.core.urlresolvers import reverse
from shop.backends_pool import backends_pool
from shop.models.ordermodel import Order
from shop.models.clientmodel import Client, Address
from shop.forms import AddressForm
from shop.util.cart import get_or_create_cart
from shop.util.order import add_order_to_request
from shop.views import ShopTemplateView

class SelectShippingView(ShopTemplateView):
    template_name = 'shop/checkout/choose_shipping.html'
    
    def create_order_object_from_cart(self):
        """
        This will create an Order object form the current cart, and will pass
        a reference to the Order on either the User object or the session.
        """
        cart = get_or_create_cart(self.request)
        cart.update()
        order = Order.objects.create_from_cart(cart)
        request = self.request
        add_order_to_request(request, order)
    
    def get_context_data(self, **kwargs):
        """
        This overrides the context from the normal template view, and triggers
        the transformation of a Cart into an Order.
        """
        ctx = super(SelectShippingView, self).get_context_data(**kwargs)
        shipping_modules_list = backends_pool.get_shipping_backends_list()
        
        self.create_order_object_from_cart()
        
        select = {}
        
        for backend in shipping_modules_list:
            url = reverse(backend.url_namespace)
            select.update({backend.backend_name:url})
        ctx.update({'shipping_options':select})
        return ctx
        

class SelectPaymentView(ShopTemplateView):
    template_name = 'shop/checkout/choose_payment.html'

    def get_context_data(self, **kwargs):
        """
        This overrides the context from the normal template view
        """
        ctx = super(SelectPaymentView, self).get_context_data(**kwargs)
        payment_modules_list = backends_pool.get_payment_backends_list()
        
        select = {}
        
        for backend in payment_modules_list:
            url = reverse(backend.url_namespace)
            select.update({backend.backend_name:url})
        ctx.update({'payment_options':select})
        return ctx

class ThankYouView(ShopTemplateView):
    template_name = 'shop/checkout/thank_you.html'

class ShippingBillingView(ShopTemplateView):
    template_name = 'shop/checkout/billingshipping.html'
    def get_context_data(self, **kwargs):
        """
        This overrides the context from the normal template view
        """
        ctx = super(ShippingBillingView, self).get_context_data(**kwargs)
        payment_modules_list = backends_pool.get_payment_backends_list()
        shipping_modules_list = backends_pool.get_shipping_backends_list()

        try:
            client = Client.objects.get(user=self.request.user)
        except Client.DoesNotExist:
            client = Client()
            client.user = self.request.user
            client.save()

        try:
            shipping_address = client.shipping_address()
        except:
            shipping_address = Address()
            shipping_address.client = client
            shipping_address.is_shipping = True
        try:
            billing_address = client.billing_address()
        except:
            billing_address = Address()
            billing_address.client = client
            billing_address.is_billing = True

        shipping_form = AddressForm(instance=shipping_address)
        billing_form = AddressForm(instance=billing_address)
        ctx.update({'shipping_address':shipping_form,'billing_address':billing_form})
        
        select = {}
        for backend in payment_modules_list:
            url = reverse(backend.url_namespace)
            select.update({backend.backend_name:url})
        ctx.update({'payment_options':select})

        select = {}
        for backend in shipping_modules_list:
            url = reverse(backend.url_namespace)
            select.update({backend.backend_name:url})
        ctx.update({'shipping_options':select})
        return ctx
