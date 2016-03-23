# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import with_metaclass
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from .order import BaseOrder, BaseOrderItem, OrderItemModel
from . import deferred


class BaseDelivery(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    Shipping provider to keep track on each delivery.
    """
    order = deferred.ForeignKey(BaseOrder)
    shipping_id = models.CharField(_("Shipping ID"), max_length=255, null=True, blank=True,
        help_text=_("The transaction processor's reference"))
    fulfilled_at = models.DateTimeField(_("Fulfilled at"), null=True, blank=True)
    shipped_at = models.DateTimeField(_("Shipped at"), null=True, blank=True)
    shipping_method = models.CharField(_("Shipping method"), max_length=50,
        help_text=_("The shipping backend used to deliver the items for this order"))

    class Meta:
        abstract = True
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")

    @classmethod
    def perform_model_checks(cls):
        canceled_field = [f for f in OrderItemModel._meta.fields if f.attname == 'canceled']
        if not canceled_field or canceled_field[0].get_internal_type() != 'BooleanField':
            msg = "Class `{}` must implement a `BooleanField` named `canceled`, if used in combination with a Delivery model."
            raise ImproperlyConfigured(msg.format(OrderItemModel.__name__))

DeliveryModel = deferred.MaterializedModel(BaseDelivery)


class BaseDeliveryItem(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    Abstract base class to keep track on the delivered quantity for each ordered item. Since the
    quantity can be any numerical value, it has to be defined by the class implementing this model.
    """
    delivery = deferred.ForeignKey(BaseDelivery, verbose_name=_("Delivery"),
        help_text=_("Refer to the shipping provider used to ship this item"))
    item = deferred.ForeignKey(BaseOrderItem, verbose_name=_("Ordered item"))

    class Meta:
        abstract = True
        verbose_name = _("Deliver item")
        verbose_name_plural = _("Deliver items")

    @classmethod
    def perform_model_checks(cls):
        try:
            order_field = [f for f in OrderItemModel._meta.fields if f.attname == 'quantity'][0]
            deliver_field = [f for f in cls._meta.fields if f.attname == 'quantity'][0]
            if order_field.get_internal_type() != deliver_field.get_internal_type():
                msg = "Field `{}.quantity` must be of one same type `{}.quantity`."
                raise ImproperlyConfigured(msg.format(cls.__name__, OrderItemModel.__name__))
        except IndexError:
            msg = "Class `{}` must implement a field named `quantity`."
            raise ImproperlyConfigured(msg.format(cls.__name__))

DeliveryItemModel = deferred.MaterializedModel(BaseDeliveryItem)
