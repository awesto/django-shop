# -*- coding: utf-8 -*-
"""
This models the checkout process using views.
"""
from django.core.urlresolvers import reverse
from django.forms import models as model_forms
from django.http import HttpResponseRedirect
from django.views.generic import RedirectView
from django.utils.functional import cached_property

from shop.forms import AddressesForm, BillingShippingForm
from shop.util.address import (
    assign_address_to_request,
    get_billing_address_from_request,
    get_shipping_address_from_request,
)
from shop.util.cart import get_or_create_cart
from shop.util.order import add_order_to_request, get_order_from_request
from shop.util.order import redirect_to_shipping
from shop.views import ShopTemplateView, ShopView
from shop.util.login_mixin import LoginMixin


class CheckoutSelectionView(LoginMixin, ShopTemplateView):
    template_name = 'shop/checkout/selection.html'

    def _get_dynamic_form_class_from_factory(self):
        """
        Returns a dynamic ModelForm from the loaded AddressModel
        """
        from shop.models import AddressModel
        form_class = model_forms.modelform_factory(
            AddressModel, exclude=['user_shipping', 'user_billing'])
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
        from shop.models.ordermodel import Order
        cart = get_or_create_cart(self.request)
        cart.update(self.request)
        order = Order.objects.create_from_cart(cart, self.request)
        add_order_to_request(self.request, order)
        return order

    @cached_property
    def addresses_form(self):
        """Creates an form which handles all the complexity behind selecting
        the two addresses
        """
        data = None
        if self.request.method == "POST":
            data = self.request.POST

        return AddressesForm(data,
            billing=get_billing_address_from_request(self.request),
            shipping=get_shipping_address_from_request(self.request),
            billing_form_class=self.get_billing_form_class(),
            shipping_form_class=self.get_shipping_form_class(),
        )

    @cached_property
    def billing_and_shipping_selection_form(self):
        """
        Get (and cache) the BillingShippingForm instance
        """
        if self.request.method == 'POST':
            return BillingShippingForm(self.request.POST)
        return BillingShippingForm()

    def save_addresses_to_order(self, order, shipping_address,
                                billing_address):
        """
        Provided for extensibility.

        Adds both addresses (shipping and billing addresses) to the Order
        object.
        """
        order.set_shipping_address(shipping_address)
        order.set_billing_address(billing_address)
        order.save()

    @cached_property
    def extra_info_form(self):
        """
        Initializes and handles the form for order extra info.
        """
        # Create a dynamic Form class for the model
        from shop.models import OrderExtraInfo
        form_class = model_forms.modelform_factory(OrderExtraInfo, exclude=['order'])
        if self.request.method == 'POST':
            return form_class(self.request.POST)
        else:
            return form_class()

    def save_extra_info_to_order(self, order, form):
        if form.cleaned_data.get('text'):
            extra_info = form.save(commit=False)
            extra_info.order = order
            extra_info.save()

    def post(self, *args, **kwargs):
        """ Called when view is POSTed """
        addresses_form = self.addresses_form  # the POST data are automatically passed to the form
        extra_info_form = self.extra_info_form
        if addresses_form.is_valid() and extra_info_form.is_valid():

            # Add the address to the order
            billing_address, shipping_address = \
                addresses_form.save_to_request(self.request)
            order = self.create_order_object_from_cart()

            self.save_addresses_to_order(order,
                shipping_address=shipping_address,
                billing_address=billing_address,)

            bs_form = self.billing_and_shipping_selection_form

            if bs_form.is_valid():
                # save selected billing and shipping methods
                order.shipping_backend = bs_form.cleaned_data['shipping_backend']
                order.payment_backend = bs_form.cleaned_data['payment_backend']
                order.save()
                # add extra info to order
                self.save_extra_info_to_order(order, extra_info_form)

                return redirect_to_shipping(self.request, order)

        return self.get(self, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        This overrides the context from the normal template view
        """
        ctx = super(CheckoutSelectionView, self).get_context_data(**kwargs)

        addresses_form = self.addresses_form
        bs_form = self.billing_and_shipping_selection_form
        extra_info_form = self.extra_info_form
        ctx.update({
            'addresses_form': addresses_form,
            'billing_shipping_form': bs_form,
            'extra_info_form': extra_info_form,
        })
        return ctx


class OrderConfirmView(RedirectView):
    url_name = 'checkout_payment'
    permanent = False

    def confirm_order(self):
        order = get_order_from_request(self.request)
        order.status = order.CONFIRMED
        order.save()

    def get(self, request, *args, **kwargs):
        self.confirm_order()
        return super(OrderConfirmView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        self.url = reverse(self.url_name)
        return super(OrderConfirmView, self).get_redirect_url(**kwargs)


class ThankYouView(LoginMixin, ShopTemplateView):
    template_name = 'shop/checkout/thank_you.html'

    def get_context_data(self, **kwargs):
        ctx = super(ShopTemplateView, self).get_context_data(**kwargs)

        # put the latest order in the context only if it is completed
        order = get_order_from_request(self.request)
        if order and order.status == order.COMPLETED:
            ctx.update({'order': order, })

        return ctx
