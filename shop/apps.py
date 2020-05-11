import warnings

from django.apps import AppConfig
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _


class ShopConfig(AppConfig):
    name = 'shop'
    verbose_name = _("Shop")
    cache_supporting_wildcard = False

    def ready(self):
        from rest_framework.serializers import ModelSerializer
        from shop.deferred import ForeignKeyBuilder
        from shop.models.fields import JSONField
        from shop.rest.fields import JSONSerializerField
        from shop.patches import PageAttribute
        from cms.templatetags import cms_tags

        # add JSONField to the map of customized serializers
        ModelSerializer.serializer_field_mapping[JSONField] = JSONSerializerField

        # perform some sanity checks
        ForeignKeyBuilder.check_for_pending_mappings()

        cms_tags.register.tags['page_attribute'] = PageAttribute

        if callable(getattr(cache, 'delete_pattern', None)):
            self.cache_supporting_wildcard = True
        else:
            warnings.warn("\n"
                "Your caching backend does not support invalidation by key pattern.\n"
                "Please use `django-redis-cache`, or wait until the product's HTML\n"
                "snippet cache expires by itself.")
