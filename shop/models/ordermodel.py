# -*- coding: utf-8 -*-
from distutils.version import LooseVersion
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _
from shop.models.productmodel import Product
from shop.util.fields import CurrencyField
from shop.util.loader import load_class
import django


#==============================================================================
# Extensibility
#==============================================================================
# This overrides the various models with classes loaded from the corresponding
# setting if it exists.

# Order model
ORDER_MODEL = getattr(settings, 'SHOP_ORDER_MODEL',
    'shop.models.defaults.order.Order')
Order = load_class(ORDER_MODEL, 'SHOP_ORDER_MODEL')

# Order item model
ORDERITEM_MODEL = getattr(settings, 'SHOP_ORDERITEM_MODEL',
    'shop.models.defaults.orderitem.OrderItem')
OrderItem = load_class(ORDERITEM_MODEL, 'SHOP_ORDERITEM_MODEL')


# Now we clear refrence to product from every OrderItem
def clear_products(sender, instance, using, **kwargs):
    for oi in OrderItem.objects.filter(product=instance):
        oi.product = None
        oi.save()

if LooseVersion(django.get_version()) < LooseVersion('1.3'):
    pre_delete.connect(clear_products, sender=Product)


class OrderExtraInfo(models.Model):
    """
    A holder for extra textual information to attach to this order.
    """
    order = models.ForeignKey(Order, related_name="extra_info",
            verbose_name=_('Order'))
    text = models.TextField(verbose_name=_('Extra info'))

    class Meta(object):
        app_label = 'shop'
        verbose_name = _('Order extra info')
        verbose_name_plural = _('Order extra info')


class ExtraOrderPriceField(models.Model):
    """
    This will make Cart-provided extra price fields persistent since we want
    to "snapshot" their statuses at the time when the order was made
    """
    order = models.ForeignKey(Order, verbose_name=_('Order'))
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    value = CurrencyField(verbose_name=_('Amount'))
    # Does this represent shipping costs?
    is_shipping = models.BooleanField(default=False, editable=False,
            verbose_name=_('Is shipping'))

    class Meta(object):
        app_label = 'shop'
        verbose_name = _('Extra order price field')
        verbose_name_plural = _('Extra order price fields')


class ExtraOrderItemPriceField(models.Model):
    """
    This will make Cart-provided extra price fields persistent since we want
    to "snapshot" their statuses at the time when the order was made
    """
    order_item = models.ForeignKey(OrderItem, verbose_name=_('Order item'))
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    value = CurrencyField(verbose_name=_('Amount'))

    class Meta(object):
        app_label = 'shop'
        verbose_name = _('Extra order item price field')
        verbose_name_plural = _('Extra order item price fields')


class OrderPayment(models.Model):
    """
    A class to hold basic payment information. Backends should define their own
    more complex payment types should they need to store more informtion
    """
    order = models.ForeignKey(Order, verbose_name=_('Order'))
    # How much was payed with this particular transfer
    amount = CurrencyField(verbose_name=_('Amount'))
    transaction_id = models.CharField(max_length=255,
            verbose_name=_('Transaction ID'),
            help_text=_("The transaction processor's reference"))
    payment_method = models.CharField(max_length=255,
            verbose_name=_('Payment method'),
            help_text=_("The payment backend use to process the purchase"))

    class Meta(object):
        app_label = 'shop'
        verbose_name = _('Order payment')
        verbose_name_plural = _('Order payments')
