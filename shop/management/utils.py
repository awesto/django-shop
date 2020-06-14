from djangocms_text_ckeditor.models import Text
from djangocms_text_ckeditor.utils import plugin_tags_to_id_list, replace_plugin_tags
from cms.api import add_plugin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.models import CascadeElement


def deserialize_to_placeholder(placeholder, data, language):
    def plugins_from_data(placeholder, parent, data):
        for plugin_type, data, children_data in data:
            try:
                plugin_class = plugin_pool.get_plugin(plugin_type)
            except Exception:
                continue
            kwargs = dict(data)
            inlines = kwargs.pop('inlines', [])
            shared_glossary = kwargs.pop('shared_glossary', None)
            try:
                instance = add_plugin(placeholder, plugin_class, language, target=parent, **kwargs)
            except Exception:
                continue
            if isinstance(instance, CascadeElement):
                instance.plugin_class.add_inline_elements(instance, inlines)
                instance.plugin_class.add_shared_reference(instance, shared_glossary)

            # for some unknown reasons add_plugin sets instance.numchild to 0,
            # but fixing and save()-ing 'instance' executes some filters in an unwanted manner
            plugins_from_data(placeholder, instance, children_data)

            if isinstance(instance, Text):
                # we must convert the old plugin IDs into the new ones,
                # otherwise links are not displayed
                id_dict = dict(zip(
                    plugin_tags_to_id_list(instance.body),
                    (t[0] for t in instance.get_children().values_list('id'))
                ))
                instance.body = replace_plugin_tags(instance.body, id_dict)
                instance.save()

    plugins_from_data(placeholder, None, data['plugins'])
