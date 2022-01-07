"""
Some models in the merchant's implementation require a many-to-many relation with models from
outside django-SHOP. Therefore these mapping tables must be materialized by the merchant's
implementation.
"""
# from shop.shopmodels.related import BaseProductPage, BaseProductImage
from shop.shopmodels.related import BaseProductImage
# from shop.shopmodels.defaults.smartcard import SmartCard
from django.db import models


# class ProductPage(BaseProductPage):
#     """Materialize many-to-many relation with CMS pages"""
#     class Meta(BaseProductPage.Meta):
#         abstract = False


class ProductImage(BaseProductImage):
    """Materialize many-to-many relation with images"""
    smart_card = models.ForeignKey(
        'SmartCard',
        on_delete=models.CASCADE,
    )
    image = models.ForeignKey(
        'filer.Image',
        on_delete=models.CASCADE,
    )

    class Meta(BaseProductImage.Meta):
        abstract = False
