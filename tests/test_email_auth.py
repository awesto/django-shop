# -*- coding: utf-8
from __future__ import unicode_literals

import pytest
from django.contrib.auth import get_user_model
from tests.testshop.models import Customer


@pytest.mark.django_db
def test_user(user_factory):
    user = user_factory(id=1)
    assert isinstance(user, get_user_model())


@pytest.mark.django_db
def test_customer(customer_factory):
    customer = customer_factory()
    assert isinstance(customer, Customer)
