from django.utils.cache import add_never_cache_headers
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from shop.models.cart import CartModel, CartItemModel
from shop.serializers.cart import CartSerializer, CartItemSerializer, WatchSerializer, WatchItemSerializer, CartItems


class BaseViewSet(viewsets.ModelViewSet):
    pagination_class = None
    with_items = CartItems.arranged

    def get_queryset(self):
        try:
            cart = CartModel.objects.get_from_request(self.request)
            if self.kwargs.get(self.lookup_field):
                # we're interest only into a certain cart item
                return CartItemModel.objects.filter(cart=cart)
            return cart
        except CartModel.DoesNotExist:
            return CartModel()

    def list(self, request, *args, **kwargs):
        cart = self.get_queryset()
        context = self.get_serializer_context()
        serializer = self.serializer_class(cart, context=context, label=self.serializer_label,
                                           with_items=self.with_items)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new item in the cart.
        """
        context = self.get_serializer_context()
        item_serializer = self.item_serializer_class(context=context, data=request.data, label=self.serializer_label)
        item_serializer.is_valid(raise_exception=True)
        self.perform_create(item_serializer)
        headers = self.get_success_headers(item_serializer.data)
        return Response(item_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Handle changing the amount of the cart item referred by its primary key.
        """
        cart_item = self.get_object()
        context = self.get_serializer_context()
        item_serializer = self.item_serializer_class(
            cart_item,
            context=context,
            data=request.data,
            label=self.serializer_label,
        )
        item_serializer.is_valid(raise_exception=True)
        self.perform_update(item_serializer)
        cart_serializer = CartSerializer(cart_item.cart, context=context, label='cart')
        response_data = {
            'cart': cart_serializer.data,
            'cart_item': item_serializer.data,
        }
        return Response(data=response_data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a cart item referred by its primary key.
        """
        cart_item = self.get_object()
        context = self.get_serializer_context()
        cart_serializer = CartSerializer(cart_item.cart, context=context, label=self.serializer_label)
        self.perform_destroy(cart_item)
        response_data = {
            'cart_item': None,
            'cart': cart_serializer.data,
        }
        return Response(data=response_data)

    def finalize_response(self, request, response, *args, **kwargs):
        """Set HTTP headers to not cache this view"""
        if self.action != 'render_product_summary':
            add_never_cache_headers(response)
        return super().finalize_response(request, response, *args, **kwargs)


class CartViewSet(BaseViewSet):
    serializer_label = 'cart'
    serializer_class = CartSerializer
    item_serializer_class = CartItemSerializer

    @action(detail=True, methods=['get'])
    def fetch(self, request):
        cart = self.get_queryset()
        context = self.get_serializer_context()
        serializer = self.serializer_class(cart, context=context, with_items=CartItems.without)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='fetch-dropdown')
    def fetch_dropdown(self, request):
        cart = self.get_queryset()
        context = self.get_serializer_context()
        serializer = self.serializer_class(cart, context=context, label='dropdown', with_items=CartItems.unsorted)
        return Response(serializer.data)


class WatchViewSet(BaseViewSet):
    serializer_label = 'watch'
    serializer_class = WatchSerializer
    item_serializer_class = WatchItemSerializer
