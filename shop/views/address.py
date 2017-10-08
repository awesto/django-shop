# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer

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
        super(AddressEditView, self).__init__(**kwargs)
        self.visible_fields = [f.name for f in self.form_class().visible_fields()]

    def get(self, request, priority=None, *args, **kwargs):
        if priority == 'add':
            # deliver an empty form
            form = self.form_class()
        else:
            try:
                instance = request.customer.shippingaddress_set.get(priority=priority)
            except CartModel.DoesNotExist:
                return Response(status=404)
            else:
                cart = CartModel.objects.get_from_request(request)
                form = self.form_class(instance=instance, cart=cart)
        initial_data = dict((k, v) for k, v in form.get_initial_data().items() if k in self.visible_fields)
        return Response({'shipping_address_form': initial_data})

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body).get(self.form_class.scope_prefix, {})
        cart = CartModel.objects.get_from_request(request)
        form = self.form_class(data=data, cart=cart)
        if form.is_valid():
            return Response()
        return Response(status=422)

    def delete(self, request, priority=None, *args, **kwargs):
        if priority != 'add':
            try:
                request.customer.shippingaddress_set.get(priority=priority).delete()
            except CartModel.DoesNotExist:
                return Response(status=404)

        # take the last of the remaining addresses
        instance = request.customer.shippingaddress_set.last()
        cart = CartModel.objects.get_from_request(request)
        form = self.form_class(instance=instance, cart=cart)
        initial_data = dict((k, v) for k, v in form.get_initial_data().items() if k in self.visible_fields)
        initial_data.update(active_priority=str(instance.priority), siblings_summary=form.siblings_summary)
        return Response({'shipping_address_form': initial_data})
