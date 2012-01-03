# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from django.db import models, transaction
from django.db.models.aggregates import Count
from polymorphic.manager import PolymorphicManager

from shop.order_signals import processing


#==============================================================================
# Product
#==============================================================================
class ProductStatisticsManager(PolymorphicManager):
    """
    A Manager for all the non-object manipulation needs, mostly statistics and
    other "data-mining" toys.
    """

    def top_selling_products(self, quantity):
        """
        This method "mines" the previously passed orders, and gets a list of
        products (of a size equal to the quantity parameter), ordered by how
        many times they have been purchased.
        """
        # Importing here is fugly, but it saves us from circular imports...
        from shop.models.ordermodel import OrderItem
        # Get an aggregate of product references and their respective counts
        top_products_data = OrderItem.objects.values(
                'product').annotate(
                    product_count=Count('product')
                ).order_by('product_count'
            )[:quantity]

        # The top_products_data result should be in the form:
        # [{'product_reference': '<product_id>', 'product_count': <count>}, ..]

        top_products_list = []  # The actual list of products
        for values in top_products_data:
            prod = values.get('product')
            # We could eventually return the count easily here, if needed.
            top_products_list.append(prod)

        return top_products_list


class ProductManager(PolymorphicManager):
    """
    A more classic manager for Product filtering and manipulation.
    """
    def active(self):
        return self.filter(active=True)


#==============================================================================
# Order
#==============================================================================

class OrderManager(models.Manager):

    def get_latest_for_user(self, user):
        """
        Returns the last Order (from a time perspective) a given user has
        placed.
        """
        if user and not isinstance(user, AnonymousUser):
            return self.filter(user=user).order_by('-modified')[0]
        else:
            return None

    @transaction.commit_on_success
    def create_from_cart(self, cart):
        """
        This creates a new Order object (and all the rest) from a passed Cart
        object.

        Specifically, it creates an Order with corresponding OrderItems and
        eventually corresponding ExtraPriceFields

        This will only actually commit the transaction once the function exits
        to minimize useless database access.

        Emits the ``processing`` signal.
        """
        # must be imported here!
        from shop.models.ordermodel import (
            ExtraOrderItemPriceField,
            ExtraOrderPriceField,
            OrderItem,
        )
        from shop.models.cartmodel import CartItem
        # Let's create the Order itself:
        order = self.model()
        order.user = cart.user
        order.status = self.model.PROCESSING  # Processing

        order.order_subtotal = cart.subtotal_price
        order.order_total = cart.total_price

        order.save()

        # Let's serialize all the extra price arguments in DB
        for label, value in cart.extra_price_fields:
            eoi = ExtraOrderPriceField()
            eoi.order = order
            eoi.label = str(label)
            eoi.value = value
            eoi.save()

        # There, now move on to the order items.
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            item.update(cart)
            order_item = OrderItem()
            order_item.order = order
            order_item.product_reference = item.product.id
            order_item.product_name = item.product.get_name()
            order_item.product = item.product
            order_item.unit_price = item.product.get_price()
            order_item.quantity = item.quantity
            order_item.line_total = item.line_total
            order_item.line_subtotal = item.line_subtotal
            order_item.save()
            # For each order item, we save the extra_price_fields to DB
            for label, value in item.extra_price_fields:
                eoi = ExtraOrderItemPriceField()
                eoi.order_item = order_item
                # Force unicode, in case it has àö...
                eoi.label = unicode(label)
                eoi.value = value
                eoi.save()

        processing.send(self.model, order=order, cart=cart)
        return order
