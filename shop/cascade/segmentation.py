# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cmsplugin_cascade.segmentation.mixins import EmulateUserModelMixin, EmulateUserAdminMixin
from shop.admin.customer import CustomerProxy


class EmulateCustomerModelMixin(EmulateUserModelMixin):
    UserModel = CustomerProxy


class EmulateCustomerAdminMixin(EmulateUserAdminMixin):
    UserModel = CustomerProxy
