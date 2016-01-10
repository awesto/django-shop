from django.conf.urls import url
from shop.payment.pay_on_delivery import pay_on_delivery
from shop.payment.credit_card import setup_view, entry_view, callback_view


urlpatterns = [
	# example URLs for simple payment
	url(r'^payment/on-delivery/$', pay_on_delivery),

	# example URLs for complicated payment backend
	url(r'payment/credit-card/', setup_view, name="credit_card"),
	url(r'payment/credit-card/send', entry_view, name="credit_card_entry"),
	url(r'payment/credit-card/receive', callback_view, name="credit_card_callback"),
]