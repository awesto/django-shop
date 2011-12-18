from django.conf.urls.defaults import url, patterns

from shop.views.checkout import (
    # SelectPaymentView,
    # SelectShippingView,
    CheckoutSelectionView,
    PaymentBackendRedirectView,
    ShippingBackendRedirectView,
    ThankYouView,
)

urlpatterns = patterns('',
    url(r'^$', CheckoutSelectionView.as_view(),
        name='checkout_selection'  # First step of the checkout process
        ),
    #url(r'^checkout/ship/$', SelectShippingView.as_view(),
    #    name='checkout_shipping'  # First step of the checkout process
    #    ),
    url(r'^ship/$', ShippingBackendRedirectView.as_view(),
        name='checkout_shipping'  # First step of the checkout process
        ),
    #url(r'^checkout/pay/$', SelectPaymentView.as_view(),
    #    name='checkout_payment'  # Second step of the checkout process
    #    ),
    url(r'^pay/$', PaymentBackendRedirectView.as_view(),
        name='checkout_payment'  # First step of the checkout process
        ),
    url(r'^thank_you/$', ThankYouView.as_view(),
        name='thank_you_for_your_order'  # Second step of the checkout process
        ),
    )
