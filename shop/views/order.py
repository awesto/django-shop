from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from shop.models.order import BaseOrder
from shop.views import ShopListView, ShopDetailView


class OrderListView(ShopListView):
    """
    Display list or orders for logged in user.
    """
    queryset = BaseOrder.materialized_model.objects.all()

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
    queryset = BaseOrder.materialized_model.objects.all()

    def get_queryset(self):
        queryset = super(OrderDetailView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderDetailView, self).dispatch(*args, **kwargs)
