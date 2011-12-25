from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from shop.views import ShopListView, ShopDetailView
from shop.models import Order, OrderItem
from shop.util.cart import get_or_create_cart
from shop.util.order import copy_order_item_to_cart


class OrderListView(ShopListView):
    """
    Display list or orders for logged in user.
    """
    queryset = Order.objects.all()

    def get_queryset(self):
        queryset = super(OrderListView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderListView, self).dispatch(*args, **kwargs)


class OrderDetailView(ShopDetailView):
    """
    Display order for logged in user.
    """
    queryset = Order.objects.all()

    def get_queryset(self):
        queryset = super(OrderDetailView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        if request.POST.has_key('copy_item_to_cart'):
            copy_order_item_to_cart(request, order, 
                                    int(request.POST['copy_item_to_cart']))
        return redirect(order)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderDetailView, self).dispatch(*args, **kwargs)
