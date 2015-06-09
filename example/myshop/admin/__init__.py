# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from shop.admin.notification import NotificationAdmin
from shop.admin.order import OrderAdmin
from shop.admin.auth import CustomerAdmin
from myshop.models import Order, Notification
from myshop.models.auth import Customer
from . import product
from . import commodity

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Notification, NotificationAdmin)
