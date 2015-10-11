# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
from django.core.cache import cache


class InvalidateProductCacheMixin(object):
    def __init__(self, *args, **kwargs):
        if not hasattr(cache, 'delete_pattern'):
            warnings.warn("Your caching backend does not support deletion by key patterns. "
                "Please use `django-redis-cache`, or wait until the product's HTML snippet cache "
                "expired by itself")
        super(InvalidateProductCacheMixin, self).__init__(*args, **kwargs)

    def save_model(self, request, product, form, change):
        if change:
            self.invalidate_cache(product)
        super(InvalidateProductCacheMixin, self).save_model(request, product, form, change)

    def invalidate_cache(self, product):
        """
        The method ``ProductCommonSerializer.render_html`` caches the rendered HTML snippets.
        Invalidate them after changing something in the product.
        """
        try:
            cache.delete_pattern('product:{}|*'.format(product.id))
        except AttributeError:
            pass
