# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import factory.fuzzy
import pytest
from pytest_factoryboy import register
from testshop.models import CommodityInventory


@register
class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommodityInventory

    @classmethod
    def create(cls, **kwargs):
        inventory = super(InventoryFactory, cls).create(**kwargs)
        return inventory

@pytest.mark.django_db
def test_sell_short(inventory_factory):
    inventory = inventory_factory()
    assert inventory
