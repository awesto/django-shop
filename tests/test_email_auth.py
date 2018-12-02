# -*- coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.django_db
def test_user(user_factory):
    user = user_factory()
    assert user.first_name == "John"


@pytest.mark.django_db
def test_customer(customer_factory):
    customer = customer_factory()
    assert customer.user.first_name == "John"
