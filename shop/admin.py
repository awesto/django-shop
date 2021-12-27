from django.contrib import admin
from shop.admin.defaults.order import OrderAdmin
from shop.admin.delivery import DeliveryOrderAdminMixin
from shop.admin.order import PrintInvoiceAdminMixin
from shop.models.defaults.order import Order


@admin.register(Order)
class OrderAdmin(PrintInvoiceAdminMixin, DeliveryOrderAdminMixin, OrderAdmin):
        pass
