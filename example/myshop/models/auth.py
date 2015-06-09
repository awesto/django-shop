# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.settings import SHOP_APP_LABEL
from shop.models.auth import BaseCustomer


class Customer(BaseCustomer):
    """
    Replace `auth.models.User` with this alternative implementation.
    """
    class Meta:
        app_label = SHOP_APP_LABEL

# Migrate from auth_user table:
# INSERT INTO myshop_customer (id,password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined) \
# SELECT id,password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined from auth_user;
