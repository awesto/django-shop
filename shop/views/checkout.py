# -*- coding: utf-8 -*-
"""
This models the checkout process using views.
"""
from django.core.urlresolvers import reverse
from django.forms import models as model_forms
from django.http import HttpResponseRedirect
from shop.forms import BillingShippingForm
from shop.models.ordermodel import Order
from shop.order_signals import completed
from shop.util.address import AddressModel, get_shipping_address_from_request, \
    assign_address_to_request, get_billing_address_from_request
from shop.util.cart import get_or_create_cart
from shop.util.order import add_order_to_request, get_order_from_request
from shop.views import ShopTemplateView, ShopView


class CheckoutSelectionView(ShopTemplateView):
    template_name = 'shop/checkout/selection.html'

    def _get_dynamic_form_class_from_factory(self):
        """
        Returns a dynamic ModelForm from the loaded AddressModel
        """
        form_class = model_forms.modelform_factory(AddressModel, 
                                                   exclude=['user_shipping', 'user_billing'])
        return form_class
    
    def get_shipping_form_class(self):
        """
        Provided for extensibility.
        """
        return self._get_dynamic_form_class_from_factory()
    
    def get_billing_form_class(self):
        """
        Provided for extensibility.
        """
        return self._get_dynamic_form_class_from_factory()

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
        return order

    def get_shipping_address_form(self):
        """
        Initializes and handles the form for the shipping address.
        AddressModel is a model of the type defined in settings.SHOP_ADDRESS_MODEL.
        
        The trick here is that we generate a ModelForm for whatever model was 
        passed to us by the SHOP_ADDRESS_MODEL setting, and us this, prefixed, as
        the shipping address form. So this can be as complex or as simple as one wants.
        
        Subclasses of this view can obviously override this method and return any 
        other form instead.
        """
        # Try to get the cached version first.
        form = getattr(self, '_shipping_form', None)
        if form:
            return form
        
        # Create a dynamic Form class for the model specified as the address model
        form_class = self.get_shipping_form_class()
        
        if self.request.method == "POST":
            form = form_class(self.request.POST, prefix="ship")
        else:
            # Try to get a shipping address instance from the request (user or session))
            shipping_address = get_shipping_address_from_request(self.request)
            # We should either have an instance, or None
            if not shipping_address:
                # The user or guest doesn't already have a favorite address.
                # Instanciate a blank one, and use this as the default value for
                # the form.
                shipping_address = AddressModel()
                # Make our new address the default for the User or Guest.
                assign_address_to_request(self.request, shipping_address, shipping=True)
                
            form = form_class(instance=shipping_address, prefix="ship")
        setattr(self, '_shipping_form', form)
        return form
    
    def get_billing_address_form(self):
        """
        Initializes and handles the form for the shipping address.
        AddressModel is a model of the type defined in settings.SHOP_ADDRESS_MODEL
        """
        # Try to get the cached version first.
        form = getattr(self, '_billing_form', None)
        if form:
            return form
        # Create a dynamic Form class for the model specified as the address model
        form_class = model_forms.modelform_factory(AddressModel,
                                                   exclude=['user_shipping', 'user_billing'])
        if self.request.method == "POST":
            form = form_class(self.request.POST, prefix="bill")
        else:
            # Try to get a shipping address instance from the request (user or session))
            billing_address = get_billing_address_from_request(self.request)
            # We should either have an instance, or None
            if not billing_address:
                # The user or guest doesn't already have a favorite address.
                # Instansiate a blank one, and use this as the default value for
                # the form.
                billing_address = AddressModel()
                # Make our new address the default for the User or Guest.
                assign_address_to_request(self.request, billing_address, shipping=False)
                
            form = form_class(instance=billing_address, prefix="bill")
        setattr(self, '_billing_form', form)
        return form
            
    def get_billing_and_shipping_selection_form(self):
        """
        Get (and cache) the BillingShippingForm instance
        """
        form = getattr(self, '_billingshipping_form', None)
        if not form:
            if self.request.method == 'POST':
                form = BillingShippingForm(self.request.POST)
            else:
                form = BillingShippingForm
            self._billingshipping_form = form
        return form

    def save_addresses_to_order(self, order, shipping_address, billing_address):
        """
        Provided for extensibility.
        Adds both addresses (shipping and billing addresses to the Order object.
        """
        kwargs = {
                  'shipping_address':shipping_address.address,
                  'shipping_city':shipping_address.city,
                  'shipping_zip_code':shipping_address.zip_code,
                  'shipping_state':shipping_address.state,
                  'shipping_country':shipping_address.country,
                  }
        if shipping_address.address2:
            kwargs.update({'shipping_address2':shipping_address.address2})
        if shipping_address.name:
            kwargs.update({'shipping_name':shipping_address.name})
            
        order.set_shipping_address(**kwargs)
        
        kwargs = {
                  'billing_address':billing_address.address,
                  'billing_city':billing_address.city,
                  'billing_zip_code':billing_address.zip_code,
                  'billing_state':billing_address.state,
                  'billing_country':billing_address.country,
                  }
        if billing_address.address2:
            kwargs.update({'billing_address2':billing_address.address2})
        if billing_address.name:
            kwargs.update({'billing_name':billing_address.name})
            
        order.set_billing_address(**kwargs)
        order.save()

    def post(self, *args, **kwargs):
        """ Called when view is POSTed """
        shipping_form = self.get_shipping_address_form()
        billing_form = self.get_billing_address_form()
        if shipping_form.is_valid() and billing_form.is_valid():
            
            # Add the address to the order
            shipping_address = shipping_form.save()
            billing_address = billing_form.save()
            order = self.create_order_object_from_cart()
            
            self.save_addresses_to_order(order, shipping_address, billing_address)
            
            billingshipping_form = self.get_billing_and_shipping_selection_form()
            if billingshipping_form.is_valid():
                self.request.session['payment_backend'] = billingshipping_form.cleaned_data['payment_method']
                self.request.session['shipping_backend'] = billingshipping_form.cleaned_data['shipping_method']
                return HttpResponseRedirect(reverse('checkout_shipping'))
        
        return self.get(self, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        This overrides the context from the normal template view
        """
        ctx = super(CheckoutSelectionView, self).get_context_data(**kwargs)

        shipping_address_form = self.get_shipping_address_form()
        billing_address_form = self.get_billing_address_form()
        billingshipping_form = self.get_billing_and_shipping_selection_form()
        ctx.update({
            'shipping_address':shipping_address_form,
            'billing_address':billing_address_form,
            'billing_shipping_form':billingshipping_form,
        })
        return ctx

class ThankYouView(ShopTemplateView):
    template_name = 'shop/checkout/thank_you.html'

    def get_context_data(self, **kwargs):
        ctx = super(ShopTemplateView, self).get_context_data(**kwargs)

        # Set the order status:
        order = get_order_from_request(self.request)
        order.status = Order.COMPLETED
        order.save()
        completed.send(sender=self, order=order)

        # Empty the customers basket, to reflect that the purchase was completed
        cart_object = get_or_create_cart(self.request)
        cart_object.empty()

        return ctx

class ShippingBackendRedirectView(ShopView):
    def get(self, *args, **kwargs):
        try:
            backend_namespace = self.request.session.pop('shipping_backend')
            return HttpResponseRedirect(reverse(backend_namespace))
        except KeyError:
            return HttpResponseRedirect(reverse('cart'))
        
class PaymentBackendRedirectView(ShopView):
    def get(self, *args, **kwargs):
        try:
            backend_namespace = self.request.session.pop('payment_backend')
            return HttpResponseRedirect(reverse(backend_namespace))
        except KeyError:
            return HttpResponseRedirect(reverse('cart'))
