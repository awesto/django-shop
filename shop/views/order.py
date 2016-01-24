from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from shop.views import ShopListView, ShopDetailView
from shop.models import Order


class UserOrdersMixin(object):
    """
    Mixin that assure user is logged in and returns queryset with
    user orders with status equal or greater than COMPLETED.
    """

    def get_queryset(self):
        queryset = super(UserOrdersMixin, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        queryset = queryset.filter(status__gte=Order.COMPLETED)
        queryset = queryset.order_by('-created')
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserOrdersMixin, self).dispatch(*args, **kwargs)


class OrderListView(UserOrdersMixin, ShopListView):
    """
    Display list or orders for logged in user.
    """
    model = Order


class OrderDetailView(UserOrdersMixin, ShopDetailView):
    """
    Display order for logged in user.
    """
    model = Order
