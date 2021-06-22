from django.test import TestCase
from cms.api import add_plugin
from cms.models import Placeholder
from shop.cascade.catalog import ShopCatalogPlugin
from rest_framework.pagination import LimitOffsetPagination
from unittest.mock import MagicMock


def get_plugin_model_instance():
    placeholder = Placeholder.objects.create(slot='test')
    model_instance = add_plugin(
        placeholder,
        ShopCatalogPlugin,
        'en',
    )
    return model_instance


class ShopCatalogPluginTests(TestCase):
    def test_plugin_context_with_auto_pagination(self):
        model_instance = get_plugin_model_instance()
        plugin_instance = model_instance.get_plugin_class_instance()
        model_instance.glossary['pagination'] = 'auto'
        context = plugin_instance.render({}, model_instance, None)
        self.assertIn('pagination', context)
        self.assertEqual(context['pagination'], 'auto')

    def test_plugin_context_will_return_pagination_with_offset_when_pagination_is_auto(self):
        model_instance = get_plugin_model_instance()
        plugin_instance = model_instance.get_plugin_class_instance()
        model_instance.glossary['pagination'] = 'auto'
        pagination = LimitOffsetPagination()
        pagination.request = 123
        pagination.get_offset = MagicMock(return_value=1)

        context = plugin_instance.render({
            'paginator': pagination
        }, model_instance, None)

        pagination.get_offset.assert_called_with(123)
        self.assertIn('pagination', context)
        self.assertEqual(context['pagination'], 'paginator')
