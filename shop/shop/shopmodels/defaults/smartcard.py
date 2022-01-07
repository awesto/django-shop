from django.db import models
# from shop.shopmodels.product import BaseProduct, BaseProductManager, CMSPageReferenceMixin
from shop.shopmodels.product import BaseProduct, BaseProductManager
from shop.shopmodels.defaults.mapping import ProductImage
from shop.money.fields import MoneyField


# class SmartCard(CMSPageReferenceMixin, BaseProduct):
class SmartCard(BaseProduct):
    product_name = models.CharField(
        max_length=255,
        verbose_name="Product Name",
    )

    # slug = models.SlugField(verbose_name="Slug")
    slug = models.SlugField()

    # caption = models.TextField(
    #     "Caption",
    #     help_text="Short description used in the catalog's list view.",
    # )
    #
    # description = models.TextField(
    #     "Description",
    #     help_text="Long description used in the product's detail view.",
    # )

    caption = models.TextField()

    description = models.TextField()

    order = models.PositiveIntegerField(
        # "Sort by",
        db_index=True,
    )

    # cms_pages = models.ManyToManyField(
    #     'cms.Page',
    #     through=ProductPage,
    #     help_text="Choose list view this product shall appear on.",
    # )

    images = models.ManyToManyField(
        'filer.Image',
        through=ProductImage,
    )

    unit_price = MoneyField(
        # "Unit price",
        decimal_places=3,
        # help_text="Net price for this product",
    )

    card_type = models.CharField(
        # "Card Type",
        choices=[(t, t) for t in ('SD', 'SDXC', 'SDHC', 'SDHC II')],
        max_length=9,
    )

    product_code = models.CharField(
        # "Product code",
        max_length=255,
        unique=True,
    )

    storage = models.PositiveIntegerField(
        # "Storage Capacity",
        # help_text="Storage capacity in GB",
    )

    class Meta:
        # verbose_name = "Smart Card"
        # verbose_name_plural = "Smart Cards"
        ordering = ['order']

    lookup_fields = ['product_code__startswith', 'product_name__icontains']

    objects = BaseProductManager()

    def get_price(self, request):
        return self.unit_price

    def __str__(self):
        return self.product_name

    @property
    def sample_image(self):
        return self.images.first()
