from django.db import transaction

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer

from shop.models.address import ShippingAddressModel, BillingAddressModel
from shop.models.cart import CartModel
from shop.rest.money import JSONRenderer


class AddressEditView(GenericAPIView):
    """
    View class to render associated addresses for the current user.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    permission_classes = (IsAuthenticated,)
    form_class = None  # must be overridde

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visible_fields = [f.name for f in self.form_class().visible_fields()]

    def get(self, request, priority=None, *args, **kwargs):
        if priority == 'add':
            # deliver an empty form
            form = self.form_class()
        else:
            try:
                if self.form_class.__name__ == 'BillingAddressForm':
                    instance = request.customer.billingaddress_set.get(priority=priority)
                elif self.form_class.__name__ == 'ShippingAddressForm':
                    instance = request.customer.shippingaddress_set.get(priority=priority)
                else:
                    raise CartModel.DoesNotExist()
            except (ShippingAddressModel.DoesNotExist, BillingAddressModel.DoesNotExist):
                return Response(status=status.HTTP_410_GONE)
            else:
                cart = CartModel.objects.get_from_request(request)
                form = self.form_class(instance=instance, cart=cart)
        initial_data = dict((k, v) for k, v in form.get_initial_data().items() if k in self.visible_fields)
        initial_data.pop('use_primary_address', None)
        return Response({self.form_class.form_name: initial_data})

    def put(self, request, *args, **kwargs):
        data = request.data.get(self.form_class.scope_prefix, {})
        cart = CartModel.objects.get_from_request(request)
        form = self.form_class(data=data, cart=cart)
        if form.is_valid():
            return Response()
        response_data = {self.form_class.form_name: dict(errors=form.errors)}
        return Response(response_data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, priority=None, *args, **kwargs):
        cart = CartModel.objects.get_from_request(request)
        with transaction.atomic():
            try:
                if self.form_class.__name__ == 'BillingAddressForm':
                    request.customer.billingaddress_set.get(priority=priority).delete()
                elif self.form_class.__name__ == 'ShippingAddressForm':
                    request.customer.shippingaddress_set.get(priority=priority).delete()
            except (ValueError, ShippingAddressModel.DoesNotExist, BillingAddressModel.DoesNotExist):
                pass

            # take the last of the remaining addresses
            if self.form_class.__name__ == 'BillingAddressForm':
                instance = request.customer.billingaddress_set.last()
                cart.billing_address = instance
            elif self.form_class.__name__ == 'ShippingAddressForm':
                instance = request.customer.shippingaddress_set.last()
                cart.shipping_address = instance
            cart.save()

        # repopulate the form with address fields from the last remaining address
        if instance:
            form = self.form_class(instance=instance, cart=cart)
            initial_data = dict((k, v) for k, v in form.get_initial_data().items() if k in self.visible_fields)
            initial_data.update(active_priority=str(instance.priority), siblings_summary=form.siblings_summary)
            return Response({self.form_class.form_name: initial_data})
        return Response(status=status.HTTP_410_GONE)
