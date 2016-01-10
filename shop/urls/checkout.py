from django.conf.urls import url
from shop.util.decorators import cart_required

from shop.views.checkout import (
    CheckoutSelectionView,
    OrderConfirmView,
    ThankYouView,
)

urlpatterns = [
    url(r'^$', cart_required(CheckoutSelectionView.as_view()),
        name='checkout_selection'  # first step of the checkout process
        ),
    url(r'^confirm/$', OrderConfirmView.as_view(),
        name='checkout_confirm'  # third step of the checkout process
        ),
    url(r'^thank_you/$', ThankYouView.as_view(),
        name='thank_you_for_your_order'  # final step of the checkout process
        ),
]
