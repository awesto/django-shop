from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, mixins
from rest_framework.exceptions import NotFound, MethodNotAllowed
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from shop.rest.money import JSONRenderer
from shop.rest.renderers import CMSPageRenderer
from shop.serializers.order import OrderListSerializer, OrderDetailSerializer
from shop.models.order import OrderModel


class OrderPagination(LimitOffsetPagination):
    default_limit = 15
    template = 'shop/templatetags/paginator.html'


class OrderPermission(BasePermission):
    """
    Allow access to a given Order if the user is entitled to.
    """
    def has_permission(self, request, view):
        if view.many and request.customer.is_visitor:
            detail = _("Only signed in customers can view their list of orders.")
            raise PermissionDenied(detail=detail)
        return True

    def has_object_permission(self, request, view, order):
        if request.user.is_authenticated:
            return order.customer.pk == request.user.pk
        if order.secret and order.secret == view.kwargs.get('secret'):
            return True
        detail = _("This order does not belong to you.")
        raise PermissionDenied(detail=detail)


class OrderView(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                generics.GenericAPIView):
    """
    Base View class to render the fulfilled orders for the current user.
    """
    renderer_classes = [CMSPageRenderer, JSONRenderer, BrowsableAPIRenderer]
    list_serializer_class = OrderListSerializer
    detail_serializer_class = OrderDetailSerializer
    pagination_class = OrderPagination
    permission_classes = [OrderPermission]
    lookup_field = lookup_url_kwarg = 'slug'
    many = True
    last_order_lapse = timezone.timedelta(minutes=15)

    def get_queryset(self):
        queryset = OrderModel.objects.all()
        if not self.request.customer.is_visitor:
            queryset = queryset.filter(customer=self.request.customer).order_by('-updated_at')
        return queryset

    def get_serializer_class(self):
        if self.many:
            return self.list_serializer_class
        return self.detail_serializer_class

    def get_renderer_context(self):
        renderer_context = super().get_renderer_context()
        if self.request.accepted_renderer.format == 'html':
            renderer_context.update(many=self.many)
            if not self.many:
                # add an extra ance to the breadcrumb to show the order number
                renderer_context.update(
                    is_last_order = self.is_last(),
                    extra_ance=self.get_object().get_number(),
                )
        return renderer_context

    def is_last(self):
        """
        Returns ``True`` if the given order is considered as the last order for its customer.
        This information may be used to distinguish between a "thank you" and a normal detail view.
        """
        assert self.many is False, "This method can be called for detail views only"
        lapse = timezone.now() - self.last_order_lapse
        current_order = self.get_object()
        last_order = self.get_queryset().first()
        return current_order.id == last_order.id and current_order.created_at > lapse

    @property
    def allowed_methods(self):
        """Restrict method "POST" only on the detail view"""
        allowed_methods = self._allowed_methods()
        if self.many:
            allowed_methods.remove('POST')
        return allowed_methods

    @never_cache
    def get(self, request, *args, **kwargs):
        if self.many:
            return self.list(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.many:
            raise MethodNotAllowed("Method POST is not allowed on Order List View")
        self.update(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except OrderModel.DoesNotExist:
            raise NotFound("No orders have been found for the current user.")

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except OrderModel.DoesNotExist:
            raise NotFound("No order has been found for the current user.")
