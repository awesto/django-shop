# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.template import Context
from django.template.loader import select_template
from django.utils import translation
from django.utils.html import strip_spaces_between_tags
from django.utils.safestring import mark_safe
from haystack import indexes


class ProductIndex(indexes.SearchIndex):
    """
    Abstract base class used to index all products for this shop
    """
    text = indexes.CharField(document=True, use_template=True)
    autocomplete = indexes.EdgeNgramField(use_template=True)
    name = indexes.CharField(stored=True, indexed=False)
    product_url = indexes.CharField(stored=True, indexed=False, model_attr='get_absolute_url')

    def prepare(self, product):
        if hasattr(product, 'translations'):
            product.set_current_language(self.language)
            with translation.override(self.language):
                data = super(ProductIndex, self).prepare(product)
        else:
            data = super(ProductIndex, self).prepare(product)
        #print data
        return data

    def prepare_name(self, product):
        """
        Retrieve name though correct translation
        """
        return product.name

    def render_html(self, product, postfix):
        """
        Render a HTML snippet to be stored inside the index database.
        """
        app_label = product._meta.app_label.lower()
        product_type = product.__class__.__name__.lower()
        params = [
            (app_label, 'search', product_type, postfix),
            (app_label, 'search', 'product', postfix),
            ('shop', 'search', 'product', postfix),
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
        return self.get_model().objects.filter(active=True)
