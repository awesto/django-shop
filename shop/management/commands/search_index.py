from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

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
        actions = (p.to_dict('de') for p in ProductModel.objects.filter(active=True).iterator())
        bulk(client, actions, index=index_name)

        s = Search(index=index_name).filter().query("match", product_name="apple")
        for hit in s:
            print(hit.product_name)
