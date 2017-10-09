# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.utils.module_loading import import_string

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cms.plugin_pool import plugin_pool

from shop.conf import app_settings
from shop.models.cart import CartModel
from shop.serializers.checkout import CheckoutSerializer
from shop.modifiers.pool import cart_modifiers_pool


class CheckoutViewSet(GenericViewSet):
    """
    View for our REST endpoint to communicate with the various forms used during the checkout.
    """
    serializer_label = 'checkout'
    serializer_class = CheckoutSerializer

    def __init__(self, **kwargs):
        super(CheckoutViewSet, self).__init__(**kwargs)
        self.dialog_forms = set([import_string(fc) for fc in app_settings.SHOP_DIALOG_FORMS])
        try:
            from shop.cascade.plugin_base import DialogFormPluginBase
        except ImproperlyConfigured:
            # cmsplugins_cascade has not been installed
            pass
        else:
            # gather form classes from Cascade plugins for our checkout views
            for p in plugin_pool.get_all_plugins():
                if issubclass(p, DialogFormPluginBase):
                    if hasattr(p, 'form_classes'):
                        self.dialog_forms.update([import_string(fc) for fc in p.form_classes])
                    if hasattr(p, 'form_class'):
                        self.dialog_forms.add(import_string(p.form_class))

    @list_route(methods=['put'], url_path='upload')
    def upload(self, request):
        """
        All forms using the AngularJS directive `shop-dialog-form` have an implicit scope containing
        an `upload()` function. This function then may be connected to any input element, say
        `ng-change="upload()"`. If such an event triggers, the scope data is send to this `upload()`
        method using an Ajax POST request. This `upload()` method then dispatches the form data
        to all forms registered through a `DialogFormPluginBase`.
        Afterwards the cart is updated, so that all cart modifiers run and adopt those changes.
        """
        # sort posted form data by plugin order
        cart = CartModel.objects.get_from_request(request)
        dialog_data = []
        for form_class in self.dialog_forms:
            if form_class.scope_prefix in request.data:
                if 'plugin_order' in request.data[form_class.scope_prefix]:
                    dialog_data.append((form_class, request.data[form_class.scope_prefix]))
                else:
                    for data in request.data[form_class.scope_prefix].values():
                        dialog_data.append((form_class, data))
        dialog_data = sorted(dialog_data, key=lambda tpl: int(tpl[1]['plugin_order']))

        # save data, get text representation and collect potential errors
        errors, checkout_summary, response_data, set_is_valid = {}, {}, {}, True  # TODO:
        with transaction.atomic():
            for form_class, data in dialog_data:
                form = form_class.form_factory(request, data, cart)
                if form.is_valid():
                    # empty error dict forces revalidation by the client side validation
                    errors[form_class.form_name] = {}
                    # keep a summary of of validated form content inside the client's $rootScope
                    checkout_summary[form_class.form_name] = form.as_text()
                else:
                    errors[form_class.form_name] = dict(errors=form.errors)
                    set_is_valid = False

                # by updating the response data, we can override the form's content
                update_data = form.get_response_data()
                if isinstance(update_data, dict):
                    response_data[form_class.form_name] = update_data
            if set_is_valid:
                cart.save()

        # add possible form errors for giving feedback to the customer
        if set_is_valid:
            return Response(response_data)
        else:
            return Response(errors, status=422)

    @list_route(methods=['get'], url_path='digest')
    def digest(self, request):
        """
        Returns the summaries of the cart and various checkout forms to be rendered in non-editable fields.
        """
        cart = CartModel.objects.get_from_request(request)
        serializer = self.serializer_class(cart, context=self.get_serializer_context(), label=self.serializer_label)
        return Response(serializer.data)

    @list_route(methods=['post'], url_path='purchase')
    def purchase(self, request):
        """
        This is the final step on converting a cart into an order object. It normally is used in
        combination with the plugin :class:`shop.cascade.checkout.ProceedButtonPlugin` to render
        a button labeled "Purchase Now".
        """
        cart = CartModel.objects.get_from_request(request)
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
