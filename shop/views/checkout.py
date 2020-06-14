from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from cms.plugin_pool import plugin_pool
from shop import messages
from shop.conf import app_settings
from shop.exceptions import ProductNotAvailable
from shop.models.cart import CartModel
from shop.serializers.checkout import CheckoutSerializer
from shop.serializers.cart import CartSerializer
from shop.modifiers.pool import cart_modifiers_pool


class CheckoutViewSet(GenericViewSet):
    """
    View for our REST endpoint to communicate with the various forms used during the checkout.
    """
    serializer_label = 'checkout'
    serializer_class = CheckoutSerializer
    cart_serializer_class = CartSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

    @action(methods=['put'], detail=False, url_path='upload')
    def upload(self, request):
        """
        Use this REST endpoint to upload the payload of all forms used to setup the checkout
        dialogs. This method takes care to dispatch the uploaded payload to each corresponding
        form.
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
        errors, response_data, set_is_valid = {}, {}, True
        with transaction.atomic():
            for form_class, data in dialog_data:
                form = form_class.form_factory(request, data, cart)
                if form.is_valid():
                    # empty error dict forces revalidation by the client side validation
                    errors[form_class.form_name] = {}
                else:
                    errors[form_class.form_name] = form.errors
                    set_is_valid = False

                # by updating the response data, we can override the form's content
                update_data = form.get_response_data()
                if isinstance(update_data, dict):
                    response_data[form_class.form_name] = update_data

            # persist changes in cart
            if set_is_valid:
                cart.save()

        # add possible form errors for giving feedback to the customer
        if set_is_valid:
            return Response(response_data)
        else:
            return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @action(methods=['get'], detail=False, url_path='digest')
    def digest(self, request):
        """
        Returns the summaries of the cart and various checkout forms to be rendered in non-editable fields.
        """
        cart = CartModel.objects.get_from_request(request)
        cart.update(request)
        context = self.get_serializer_context()
        checkout_serializer = self.serializer_class(cart, context=context, label=self.serializer_label)
        cart_serializer = self.cart_serializer_class(cart, context=context, label='cart')
        response_data = {
            'checkout_digest': checkout_serializer.data,
            'cart_summary': cart_serializer.data,
        }
        return Response(data=response_data)

    @action(methods=['post'], detail=False, url_path='purchase')
    def purchase(self, request):
        """
        This is the final step on converting a cart into an order object. It normally is used in
        combination with the plugin :class:`shop.cascade.checkout.ProceedButtonPlugin` to render
        a button labeled "Purchase Now".
        """
        cart = CartModel.objects.get_from_request(request)
        try:
            cart.update(request, raise_exception=True)
        except ProductNotAvailable as exc:
            message = _("The product '{product_name}' ({product_code}) suddenly became unavailable, "\
                        "presumably because someone else has been faster purchasing it.\n Please "\
                        "recheck the cart or add an alternative product and proceed with the checkout.").\
                       format(product_name=exc.product.product_name, product_code=exc.product.product_code)
            messages.error(request, message, title=_("Product Disappeared"), delay=10)
            message = _("The product '{product_name}' ({product_code}) suddenly became unavailable.").\
                       format(product_name=exc.product.product_name, product_code=exc.product.product_code)
            response_data = {'purchasing_error_message': message}
            return Response(data=response_data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        cart.save()

        response_data = {}
        try:
            # Iterate over the registered modifiers, and search for the active payment service provider
            for modifier in cart_modifiers_pool.get_payment_modifiers():
                if modifier.is_active(cart.extra.get('payment_modifier')):
                    expression = modifier.payment_provider.get_payment_request(cart, request)
                    response_data.update(expression=expression)
                    break
        except ValidationError as err:
            message = _("Please select a valid payment method.")
            messages.warning(request, message, title=_("Choose Payment Method"), delay=5)
            response_data = {'purchasing_error_message': '. '.join(err.detail)}
            return Response(data=response_data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(data=response_data)
