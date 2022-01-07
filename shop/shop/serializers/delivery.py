from rest_framework import serializers
from shop.conf import app_settings
from shop.shopmodels.delivery import DeliveryModel, DeliveryItemModel
# from shop.shopmodels.defaults.delivery import Delivery
# from shop.shopmodels.defaults.delivery import DeliveryItem, Delivery
from shop.shopmodifiers.pool import cart_modifiers_pool


class DeliveryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryItemModel
        # model = DeliveryItem
        exclude = ['id', 'delivery', 'item']

    def to_representation(self, instance):
        data = app_settings.ORDER_ITEM_SERIALIZER(instance.item, context=self.context).data
        data['ordered_quantity'] = data.pop('quantity', None)
        data.update(super().to_representation(instance))
        return data


class DeliverySerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(
        many=True,
        read_only=True,
    )

    number = serializers.CharField(source='get_number')
    shipping_method = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryModel
        # model = Delivery
        exclude = ['id', 'order']

    def get_shipping_method(self, instance):
        for shipping_modifier in cart_modifiers_pool.get_shipping_modifiers():
            value, label = shipping_modifier.get_choice()
            if value == shipping_modifier.identifier:
                break
        else:
            value, label = instance.shipping_method, instance.shipping_method
        return {'value': value, 'label': label}
