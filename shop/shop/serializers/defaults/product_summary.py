from rest_framework import serializers
from shop.serializers.bases import ProductSerializer


class ProductSummarySerializer(ProductSerializer):
    """
    Default serializer to create a summary from our Product model. This summary then is used to
    render various list views, such as the catalog-, the cart-, and the list of ordered items.
    In case the Product model is polymorphic, this shall serialize the smallest common denominator
    of all product information.
    """
    media = serializers.SerializerMethodField(
        help_text="Returns a rendered HTML snippet containing a sample image among other elements",
    )

    caption = serializers.SerializerMethodField(
        help_text="Returns the content from caption field if available",
    )

    class Meta(ProductSerializer.Meta):
        fields = ['id', 'product_name', 'product_url', 'product_model', 'price', 'media', 'caption']

    def get_media(self, product):
        return self.render_html(product, 'media')

    def get_caption(self, product):
        return getattr(product, 'caption', None)
