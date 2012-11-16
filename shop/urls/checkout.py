from django.conf.urls.defaults import url, patterns
from shop.util.decorators import cart_required

from shop.views.checkout import (
    CheckoutSelectionView,
    PaymentBackendRedirectView,
    ShippingBackendRedirectView,
    OrderConfirmView,
    ThankYouView,
)

urlpatterns = patterns('',
    url(r'^$', cart_required(CheckoutSelectionView.as_view()),
        name='checkout_selection'  # first step of the checkout process
        ),
    url(r'^ship/$', ShippingBackendRedirectView.as_view(),
        name='checkout_shipping'  # second step of the checkout process
        ),
    url(r'^confirm/$', OrderConfirmView.as_view(),
        name='checkout_confirm'  # third step of the checkout process
        ),
    url(r'^pay/$', PaymentBackendRedirectView.as_view(),
        name='checkout_payment'  # fourth step of the checkout process
        ),
    url(r'^thank_you/$', ThankYouView.as_view(),
        name='thank_you_for_your_order'  # final step of the checkout process
        ),
    )
