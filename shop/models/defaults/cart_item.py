from django.db.models import PositiveIntegerField
from shop.models import cart


class CartItem(cart.BaseCartItem):
    """Default materialized model for CartItem"""
    quantity = PositiveIntegerField()
