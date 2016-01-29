# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.module_loading import import_by_path
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError
from cms.plugin_pool import plugin_pool
from shop.cascade.plugin_base import DialogFormPluginBase
from shop.rest.serializers import CheckoutSerializer
from shop.modifiers.pool import cart_modifiers_pool
from .cart import BaseViewSet


class CheckoutViewSet(BaseViewSet):
    serializer_label = 'checkout'
    serializer_class = CheckoutSerializer
    item_serializer_class = None

    def __init__(self, **kwargs):
        super(CheckoutViewSet, self).__init__(**kwargs)
        self.dialog_forms = []
        for p in plugin_pool.get_all_plugins():
            if issubclass(p, DialogFormPluginBase):
                self.dialog_forms.append(import_by_path(p.form_class))

    @list_route(methods=['post'], url_path='upload')
    def upload(self, request):
        """
        All forms using the AngularJS directive `shop-dialog-form` have an implicit scope containing
        an `upload()` function. This function then may be connected to any input element, say
        `ng-change="upload()"`. If such an event triggers, the scope data is send to this `upload()`
        method using an Ajax POST request. This `upload()` method then dispatches the form data
        to all forms registered through a `DialogFormPluginBase`.
        Afterwards the cart is updated, so that all cart modifiers run and adopt those changes.
        """
        cart = self.get_queryset()
        if cart is None:
            raise ValidationError("Can not proceed to checkout without a cart")

        # sort posted form data by plugin order
        dialog_data = []
        for fc in self.dialog_forms:
            key = fc.scope_prefix.split('.', 1)[1]
            if key in request.data:
                if 'plugin_order' in request.data[key]:
                    dialog_data.append((fc, request.data[key]))
                else:
                    for data in request.data[key].values():
                        dialog_data.append((fc, data))
        dialog_data = sorted(dialog_data, key=lambda tpl: int(tpl[1]['plugin_order']))

        # save data and collect potential errors
        errors = {}
        for form_class, data in dialog_data:
            reply = form_class.form_factory(request, data, cart)
            if isinstance(reply, dict):
                errors.update(reply)

        cart.save()

        # add possible form errors for giving feedback to the customer
        response = self.list(request)
        response.data.update(errors=errors)
        return response

    @list_route(methods=['post'], url_path='purchase')
    def purchase(self, request):
        """
        This is the final step on converting a cart into an order object. It normally is used in
        combination with the AngularJS directive `shop-dialog-proceed` used in combination with
        `proceedWith("PURCHASE_NOW")`.
        Use the plugin `shop.cascade.checkout.ProceedButtonPlugin` to render such a button into
        any placeholder field.
        """
        cart = self.get_queryset()
        if cart is None:
            raise ValidationError("Can not purchase without a cart")
        cart.update(request)
        cart.save()

        response = self.list(request)
        # Iterate over the registered modifiers, and search for the active payment service provider
        for modifier in cart_modifiers_pool.get_payment_modifiers():
            if modifier.is_active(cart):
                payment_provider = getattr(modifier, 'payment_provider', None)
                if payment_provider:
                    expression = payment_provider.get_payment_request(cart, request)
                    response.data.update(expression=expression)
                break
        return response
