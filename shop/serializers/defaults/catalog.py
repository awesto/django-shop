from rest_framework import serializers
from rest_framework.fields import empty
from shop.models.cart import CartModel
from shop.rest.money import MoneyField
from shop.serializers.bases import AvailabilitySerializer


class AddToCartSerializer(serializers.Serializer):
    """
    By default, this serializer is used by the view class :class:`shop.views.catalog.AddToCartView`,
    which handles the communication from the "Add to Cart" dialog box.

    If a product has variations, which influence the fields in the "Add to Cart" dialog box, then
    this serializer shall be overridden by a customized implementation. Such a customized "*Add to
    Cart*" serializer has to be connected to the ``AddToCartView``. This usually is achieved in
    the projects ``urls.py`` by changing the catalog's routing to:
    ```
    urlpatterns = [
        ...
        url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view(
            serializer_class=CustomAddToCartSerializer,
        )),
        ...
    ]
    ```
    """
    quantity = serializers.IntegerField(default=1, min_value=1)
    unit_price = MoneyField(read_only=True)
    subtotal = MoneyField(read_only=True)
    product = serializers.IntegerField(read_only=True, help_text="The product's primary key")
    product_code = serializers.CharField(read_only=True, help_text="Exact product code of the cart item")
    extra = serializers.DictField(read_only=True, default={})
    is_in_cart = serializers.BooleanField(read_only=True, default=False)
    availability = AvailabilitySerializer(read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        context = kwargs.get('context', {})
        if 'product' in context:
            instance = self.get_instance(context, data, kwargs)
            if data is not empty and 'quantity' in data:
                quantity = self.fields['quantity'].to_internal_value(data['quantity'])
            else:
                quantity = self.fields['quantity'].default
            instance.setdefault('quantity', quantity)
            super().__init__(instance, data, context=context)
        else:
            super().__init__(instance, data, **kwargs)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['quantity'] = self._validated_data['quantity']
        except AttributeError:
            data['quantity'] = self.validate_quantity(data['quantity'])
        data['subtotal'] = MoneyField().to_representation(data['quantity'] * instance['unit_price'])
        return data

    def validate_quantity(self, quantity):
        """
        Restrict the quantity allowed putting into the cart to the available quantity in stock.
        """
        availability = self.instance['availability']
        return min(quantity, availability.quantity)

    def get_instance(self, context, data, extra_args):
        """
        Method to store the ordered products in the cart item instance.
        Remember to override this method, if the ``product_code`` is part of the
        variation rather than being part of the product itself.
        """
        product = context['product']
        request = context['request']
        try:
            cart = CartModel.objects.get_from_request(request)
        except CartModel.DoesNotExist:
            cart = None
        extra = data.get('extra', {}) if data is not empty else {}
        return {
            'product': product.id,
            'product_code': product.product_code,
            'unit_price': product.get_price(request),
            'is_in_cart': bool(product.is_in_cart(cart)),
            'extra': extra,
            'availability': product.get_availability(request, **extra),
        }
