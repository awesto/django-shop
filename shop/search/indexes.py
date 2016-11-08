# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.template import Context
from django.template.loader import select_template
from django.utils import translation
from django.utils.html import strip_spaces_between_tags
from django.utils.safestring import mark_safe
from haystack import indexes
from shop.models.product import ProductModel


class ProductIndex(indexes.SearchIndex):
    """
    Abstract base class used to index all products for this shop
    """
    text = indexes.CharField(document=True, use_template=True)
    autocomplete = indexes.EdgeNgramField(use_template=True)
    product_name = indexes.CharField(stored=True, indexed=False, model_attr='product_name')
    product_url = indexes.CharField(stored=True, indexed=False, model_attr='get_absolute_url')

    def get_model(self):
        """
        Hook to refer to the used Product model. Override this to create indices of
        specialized product models.
        """
        return ProductModel

    def prepare(self, product):
        if hasattr(product, 'translations'):
            product.set_current_language(self.language)
        with translation.override(self.language):
            data = super(ProductIndex, self).prepare(product)
        return data

    def render_html(self, prefix, product, postfix):
        """
        Render a HTML snippet to be stored inside the index database, so that rendering of the
        product's list views can be performed without database queries.
        """
        app_label = product._meta.app_label.lower()
        params = [
            (app_label, prefix, product.product_model, postfix),
            (app_label, prefix, 'product', postfix),
            ('shop', prefix, 'product', postfix),
        ]
        template = select_template(['{0}/products/{1}-{2}-{3}.html'.format(*p) for p in params])
        context = Context({'product': product})
        content = strip_spaces_between_tags(template.render(context).strip())
        return mark_safe(content)

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        if using in dict(settings.LANGUAGES):
            self.language = using
        else:
            self.language = settings.LANGUAGE_CODE
        return self.get_model().objects.indexable()
