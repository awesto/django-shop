# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from shop.money import Money, MoneyMaker

from djangocms_text_ckeditor.fields import HTMLField

from shop.money.fields import MoneyField

from .product import Product, BaseProductManager


@python_2_unicode_compatible
class OperatingSystem(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=50,
    )

    def __str__(self):
        return self.name


class SmartPhoneModel(Product):
    """
    A generic smart phone model, which must be concretized by a model `SmartPhone` - see below.
    """
    BATTERY_TYPES = (
        (1, "Lithium Polymer (Li-Poly)"),
        (2, "Lithium Ion (Li-Ion)"),
    )
    WIFI_CONNECTIVITY = (
        (1, "802.11 b/g/n"),
    )
    BLUETOOTH_CONNECTIVITY = (
        (1, "Bluetooth 4.0"),
        (2, "Bluetooth 3.0"),
        (3, "Bluetooth 2.1"),
    )
    battery_type = models.PositiveSmallIntegerField(
        _("Battery type"),
        choices=BATTERY_TYPES,
    )

    battery_capacity = models.PositiveIntegerField(
        _("Capacity"),
        help_text=_("Battery capacity in mAh"),
    )

    ram_storage = models.PositiveIntegerField(
        _("RAM"),
        help_text=_("RAM storage in MB"),
    )

    wifi_connectivity = models.PositiveIntegerField(
        _("WiFi"),
        choices=WIFI_CONNECTIVITY,
        help_text=_("WiFi Connectivity"),
    )

    bluetooth = models.PositiveIntegerField(
        _("Bluetooth"),
        choices=BLUETOOTH_CONNECTIVITY,
        help_text=_("Bluetooth Connectivity"),
    )

    gps = models.BooleanField(
        _("GPS"),
        default=False,
        help_text=_("GPS integrated"),
    )

    operating_system = models.ForeignKey(
        OperatingSystem,
        verbose_name=_("Operating System"),
    )

    width = models.DecimalField(
        _("Width"),
        max_digits=4,
        decimal_places=1,
        help_text=_("Width in mm"),
    )

    height = models.DecimalField(
        _("Height"),
        max_digits=4,
        decimal_places=1,
        help_text=_("Height in mm"),
    )

    weight = models.DecimalField(
        _("Weight"),
        max_digits=5,
        decimal_places=1,
        help_text=_("Weight in gram"),
    )

    screen_size = models.DecimalField(
        _("Screen size"),
        max_digits=4,
        decimal_places=2,
        help_text=_("Diagonal screen size in inch"),
    )

    description = HTMLField(
        verbose_name=_("Description"),
        configuration='CKEDITOR_SETTINGS_DESCRIPTION',
        help_text=_("Full description used in the catalog's detail view of Smart Phones."),
    )

    default_manager = BaseProductManager()

    class Meta:
        verbose_name = _("Smart Phone")
        verbose_name_plural = _("Smart Phones")

    def get_price(self, request):
        """
        Return the starting price for instances of this smart phone model.
        """
        if not hasattr(self, '_price'):
            if self.smartphone_set.exists():
                currency = self.smartphone_set.first().unit_price.currency
                aggr = self.smartphone_set.aggregate(models.Min('unit_price'))
                self._price = MoneyMaker(currency)(aggr['unit_price__min'])
            else:
                self._price = Money()
        return self._price

    def is_in_cart(self, cart, watched=False, **kwargs):
        from shop.models.cart import CartItemModel
        try:
            product_code = kwargs['extra']['product_code']
        except KeyError:
            return
        cart_item_qs = CartItemModel.objects.filter(cart=cart, product=self)
        for cart_item in cart_item_qs:
            if cart_item.extra.get('product_code') == product_code:
                return cart_item

    def get_product_variant(self, product_code):
        try:
            return self.smartphone_set.get(product_code=product_code)
        except SmartPhone.DoesNotExist as e:
            raise SmartPhoneModel.DoesNotExist(e)


class SmartPhone(models.Model):
    product = models.ForeignKey(
        SmartPhoneModel,
        verbose_name=_("Smart-Phone Model"),
    )

    product_code = models.CharField(
        _("Product code"),
        max_length=255,
        unique=True,
    )

    unit_price = MoneyField(
        _("Unit price"),
        decimal_places=3,
        help_text=_("Net price for this product"),
    )

    storage = models.PositiveIntegerField(
        _("Internal Storage"),
        help_text=_("Internal storage in MB"),
    )

    def get_price(self, request):
        return self.unit_price
