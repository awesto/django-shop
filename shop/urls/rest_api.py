from django.conf.urls import url, include
from django.http import JsonResponse
from rest_framework import routers

from shop.forms.checkout import ShippingAddressForm, BillingAddressForm
from shop.messages import get_messages_as_json
from shop.views.address import AddressEditView
from shop.views.cart import CartViewSet, WatchViewSet
from shop.views.checkout import CheckoutViewSet
from shop.views.catalog import ProductSelectView

router = routers.DefaultRouter()  # TODO: try with trailing_slash=False
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'watch', WatchViewSet, basename='watch')
router.register(r'checkout', CheckoutViewSet, basename='checkout')


def fetch_messages(request):
    data = get_messages_as_json(request)
    return JsonResponse({'django_messages': data})


urlpatterns = [
    url(r'^select_product/?$',
        ProductSelectView.as_view(),
        name='select-product'),
    url(r'^fetch_messages/?$',
        fetch_messages,
        name='fetch-messages'),
    url(r'^shipping_address/(?P<priority>({{\s*\w+\s*}}|\d+|add))$',
        AddressEditView.as_view(form_class=ShippingAddressForm),
        name='edit-shipping-address'),
    url(r'^billing_address/(?P<priority>({{\s*\w+\s*}}|\d+|add))$',
        AddressEditView.as_view(form_class=BillingAddressForm),
        name='edit-billing-address'),
    url(r'^', include(router.urls)),
]
