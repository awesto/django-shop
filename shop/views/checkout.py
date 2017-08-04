# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.utils.module_loading import import_string

from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError

from cms.plugin_pool import plugin_pool

from shop import app_settings
from shop.serializers.cart import CheckoutSerializer
from shop.modifiers.pool import cart_modifiers_pool
from shop.views.cart import BaseViewSet


class CheckoutViewSet(BaseViewSet):
    serializer_label = 'checkout'
    serializer_class = CheckoutSerializer
    item_serializer_class = None

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
        for form_class in self.dialog_forms:
            key = form_class.scope_prefix.split('.', 1)[1]
            if key in request.data:
                if 'plugin_order' in request.data[key]:
                    dialog_data.append((form_class, request.data[key]))
                else:
                    for data in request.data[key].values():
                        dialog_data.append((form_class, data))
        dialog_data = sorted(dialog_data, key=lambda tpl: int(tpl[1]['plugin_order']))

        # save data, get text representation and collect potential errors
        errors, checkout_summary, response_data = {}, {}, {'$valid': True}
        with transaction.atomic():
            # only validates the relevant submitted checkout page form data
            for form_class, data in dialog_data:
                # payment & shipping method forms call cart.update(request) which runs all modifiers
                form = form_class.form_factory(request, data, cart)
                if form.is_valid():
                    # empty error dict forces revalidation by the client side validation
                    errors[form_class.form_name] = {}
                    # keep a summary of of validated form content inside the client's $rootScope
                    checkout_summary[form_class.form_name] = form.as_text()
                else:
                    errors[form_class.form_name] = dict(form.errors)
                response_data['$valid'] = response_data['$valid'] and form.is_valid()

                # by updating the response data, we can override the form's model $scope
                update_data = form.get_response_data()
                if isinstance(update_data, dict):
                    key = form_class.scope_prefix.split('.', 1)[1]
                    response_data[key] = update_data
            cart.save()

        # produces a response with correct cart contents by running all modifiers via cart.update(request)
        response = self.list(request)
        # adds the rest of the data for the checkout forms including customer feedback errors
        response.data.update(errors=errors, checkout_summary=checkout_summary, data=response_data)
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
        if cart.pk is None:
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
