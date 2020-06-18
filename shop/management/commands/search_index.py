from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string
from django.utils.translation import override as translation_override

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import connections, Index, Search

from shop.models.product import ProductModel


class Command(BaseCommand):
    help = "Iterates over all Product models and populate the search index."

    def handle(self, verbosity, *args, **options):
        self.verbosity = verbosity

        connections.configure(**settings.ELASTICSEARCH_DSL)
        client = Elasticsearch()
        index_name = '.'.join((settings.SHOP_APP_LABEL, 'product'))
        index = Index(index_name)
        index.document(import_string('.'.join((settings.SHOP_APP_LABEL, 'search', 'ProductDocument'))))
        bulk(client, self.index_products(), index=index_name)
        s = Search(index=index_name).filter('term', language='de').query("match", product_name="apple")
        for hit in s:
            print(hit.product_name)
        s = Search(index=index_name).filter('term', language='en').query("match", product_name="samsung")
        for hit in s:
            print(hit.product_name)

    def index_products(self):
        for language, _ in settings.LANGUAGES[:1]:
            with translation_override(language):
                for product in ProductModel.objects.filter(active=True).iterator():
                    result = product.to_dict()
                    result.update(language=language)
                    yield result
