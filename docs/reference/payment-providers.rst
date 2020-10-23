.. _reference/payment-providers:

=================
Payment Providers
=================

Payment Providers are simple classes, which create an interface from an external `Payment Service
Provider`_ (shortcut PSP) to our **django-SHOP** framework.

Payment Providers must be aggregates of a :ref:`reference/payment-cart-modifier`. Here the Payment
Cart Modifier computes extra fees when selected as a payment method, whereas our Payment Provider
class, handles the communication with the configured PSP, whenever the customer submits the purchase
request.

In **django-SHOP** Payment Providers normally are packed into separate plugins, so here we will
show how to create one yourself instead of explaining the configuration of an existing Payment
gateway.

A precautionary measure during payments with credit cards is, that the used e-commerce
implementation never sees the card numbers or any other sensible information. Otherwise those
merchants would have to be `PCI-DSS certified`_, which is an additional, but often unnecessary
bureaucratic task, since most PSPs handle that task for us.


Checkout Forms
==============

Since the merchant is not allowed to "see" sensitive credit card information, some Payment Service
Providers require, that customers are redirected to their site so that there, they can enter their
credit card numbers. This for some customers is disturbing, because they visually leave the current
shop site.

Therefore other PSPs allow to create form elements in HTML, whose content is send to their site
during the purchase task. This can be done using a POST submission, followed by a redirection back
to the client. Other providers use Javascript for submission and return a payment token to the
customer, which itself forwards that token to the shopping site.

All in all, there are so many different ways to do online payment, that it is quite tricky to find
a generic solution compatible for all of them.

In **django-SHOP**, we can add some Javascript specific to the PSP's needs, which is used during the
purchase operation. Let's explain how it works:


.. _reference/the-purchasing-operation:

The Purchasing Operation
------------------------

During checkout, the clients final step is to click onto a button labeled something like "Buy Now".
This button belongs to an AngularJS controller, provided by the directive ``shop-dialog-proceed``.
It may look similar to this:

.. code-block:: html+django

	<button shop-dialog-proceed ng-click="proceedWith('PURCHASE_NOW')" class="btn btn-success">Buy Now</button>

Whenever the customer clicks onto that button, the function ``proceedWith('PURCHASE_NOW')`` is
invoked in the scope of the AngularJS controller, belonging to the given directive.

This function first uploads the current checkout forms to the server. There the form is validated,
and if everything is OK, an updated checkout context is send back to the client. For implementation
details, have a look at the endpoint at :meth:`shop.views.checkout.CheckoutViewSet.upload()`.

Next, the success handler of the previous submission looks at the given action. In ``proceedWith``,
we used the magic keyword ``PURCHASE_NOW``, which starts a second submission to the server,
requesting to begin with the purchase operation (see
:meth:`shop.views.checkout.CheckoutViewSet.purchase()` for details.). This method determines the
payment provider previously chosen by the customer. It then invokes the method
``get_payment_request()`` of that provider, which returns a Javascript expression.

On the client, this returned Javascript expression is passed to the `eval()`_ function and executed;
it then normally starts to submit the payment request, sending all credit card data to the given
PSP.

While processing the payment, PSPs usually need to communicate with the shop framework, in order to
inform us about success or failure of the payment. To communicate with us, they may need a few
endpoints. Each class inheriting from :class:`shop.shop.payment.providers.PaymentProvider` may
override the method ``get_urls()`` returning a list of urlpatterns, which then is used by the
Django URL resolving engine.

.. code-block:: python

	from shop.payment.providers import PaymentProvider

	class MyPSP(PaymentProvider):
	    namespace = 'my-psp-payment'

	    def get_urls(self):
	        urlpatterns = [
	            url(r'^success$', self.success_view, name='success'),
	            url(r'^failure$', self.failure_view, name='failure'),
	        ]
	        return urlpatterns

	    def get_payment_request(self, cart, request):
	        js_expression = 'scope.charge().then(function(response) { $window.location.href=response.data.thank_you_url; });'
	        return js_expression

	    @classmethod
	    def success_view(cls, request):
	        # approve payment using request data returned by PSP
	        cart = CartModel.objects.get_from_request(request)
	        order = OrderModel.objects.create_from_cart(cart, request)
	        order.populate_from_cart(cart, request)
	        order.add_paypal_payment(payment.to_dict())
	        order.save(with_notification=True)
	        return HttpResponseRedirect(order.get_abolute_url())

	    @classmethod
	    def failure_view(cls, request):
	        """Redirect onto an URL informing the customer about a failed payment"""
	        cancel_url = Page.objects.public().get(reverse_id='cancel-payment').get_absolute_url()
	        return HttpResponseRedirect(cancel_url)

.. note:: The directive ``shop-dialog-proceed`` evaluates the returned Javascript expression inside
	a chained ``then(...)``-handler from the AngularJS `promise framework`_. This means that such a
	function may itself return a new promise, which is resolved by the next ``then()``-handler.

As we can see in this example, by evaluating arbitrary Javascript on the client, combined with
HTTP-handlers for any endpoint, **django-SHOP** is able to offer an API where adding new Payment
Service Providers doesn't require any special tricks.

.. _Payment Service Provider: https://en.wikipedia.org/wiki/Payment_service_provider
.. _PCI-DSS certified: https://www.pcicomplianceguide.org/pci-faqs-2/
.. _eval(): https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval
.. _promise framework: https://docs.angularjs.org/api/ng/service/$q
