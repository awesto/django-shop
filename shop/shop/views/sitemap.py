from django.contrib.sitemaps import Sitemap
# from shop.models.product import ProductModel
from shop.shopmodels.product import BaseProduct


class ProductsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    i18n = True

    def items(self):
        # return ProductModel.objects.all()
        return BaseProduct.objects.all()
