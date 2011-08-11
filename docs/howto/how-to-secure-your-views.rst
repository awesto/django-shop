.. _how-to-secure-your-views:

=========================
How to secure your views
=========================

Chances are that you don't want to allow your users to browse all views of
the shop as anonymous users. If you set ``SHOP_FORCE_LOGIN`` to ``True``, your
users will need to login before proceeding to checkout.

When you add your own shipping and payment backends you will want to add this
security mechanism as well. The problem is that the well known 
``@login_required`` decorator will not work on class based views and it will
also not work on functions that are members of a class.

For your convenience we provide three utilities that will help you to secure
your views:

@on_method decorator
=====================

This decorator can be wrapped around any other decorator. It should be used
on functions that are members of classes and will ignore the first parameter
``self`` and regard the second parameter as the first instead. More information
can be found `here <http://www.toddreed.name/content/django-view-class/>`_.

Usage::

    from shop.util.decorators import on_method, shop_login_required

    class PayOnDeliveryBackend(object):

        backend_name = "Pay On Delivery"
        url_namespace = "pay-on-delivery"

        [...]

        @on_method(shop_login_required)
        def simple_view(self, request):
            [...]
        
@shop_login_required decorator
===============================

This decorator does the same as `Django's @login_required decorator 
<https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.decorators.login_required>`_
. The only difference is that it checks for the ``SHOP_FORCE_LOGIN`` setting.
If that setting is ``False``, login will not be required.

LoginMixin class
=================

If you are using class based views for anything related to the shop you can use
:class:`shop.util.login_mixin.LoginMixin` to secure your views. More information
on this can be found
`here <https://groups.google.com/d/msg/django-users/g2E_6ZYN_R0/tnB9b262lcAJ>`_.
We are using a slightly modified version of that
:class:`~shop.util.login_mixin.LoginMixin` that makes sure to check for the
``SHOP_FORCE_LOGIN`` setting.

Usage::

    class CheckoutSelectionView(LoginMixin, ShopTemplateView):
        template_name = 'shop/checkout/selection.html'

        [...]

