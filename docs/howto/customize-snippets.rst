.. _customize-snippets:

============================
Add Customized HTML Snippets
============================

When working in *Structure Mode* as provided by **djangoCMS**, while editing the DOM tree inside a
placeholder, we might want to add a HTML snippet which is not part of the **Cascade** ecosystem.
Instead of creating an additional Django template, it often is much easier to just add a  customized
plugin. This plugin then is available when editing a placeholder in *Structure Mode*.


Customized Cascade plugin
=========================

Creating a customized plugin for the merchant's implementaion of that e-commerce project is very
easy. Just add this small Python module:

.. code-block:: python
	:caption: myshop/cascade.py

	from cms.plugin_pool import plugin_pool
	from shop.cascade.plugin_base import ShopPluginBase
	
	class MySnippetPlugin(ShopPluginBase):
	    name = "My Snippet"
	    render_template = 'myshop/cascade/my-snippet.html'
	
	plugin_pool.register_plugin(MySnippetPlugin)

then, in the project's ``settings.py`` register that plugin together with all other **Cascade**
plugins:

.. code-block:: python
	:emphasize-lines: 7

	CMSPLUGIN_CASCADE_PLUGINS = (
	    'cmsplugin_cascade.segmentation',
	    'cmsplugin_cascade.generic',
	    'cmsplugin_cascade.link',
	    'shop.cascade',
	    'cmsplugin_cascade.bootstrap3',
	    'myshop.cascade',
	    ...
	)

The template itself ``myshop/cascade/my-snippet.html`` can contain all templatetags as configured
within the Django project.

Often we want to associate customized styles and/or scripts to work with our new template. Since we
honor the principle of encapsulation_, we somehow must refer to these files in a generic way. This
is where django-sekizai_ helps us:

.. code-block:: django
	:caption: myshop/cascade/my-snippet.html

	{% load static sekizai_tags %}
	
	{% addtoblock "css" %}<link href="{% static 'myshop/css/my-snippet.css' %}" rel="stylesheet" type="text/css" />{% endaddtoblock %}
	{% addtoblock "js" %}<script src="{% static 'myshop/js/my-snippet.js' %}" type="text/javascript"></script>{% endaddtoblock %}
	
	<div>
	    my snippet code goes here...
	</div>

.. note:: The main rendering template requires a block such as ``{% render_block "css" %}`` and
	``{% render_block "js" %}`` which then displays the stylesheets and scripts inside the
	appropriate HTML elements.


Further customizing the plugin
------------------------------

Sometimes we require additional parameters which shall be customizable by the merchant, while
editing the plugin. For **Cascade** this can be achieved very easily. First think about what kind of
data to store, and which form widgets are appropriate for that kind of editor. Say we want to add
a text field holding the snippets title, then change the change the plugin code from above to:

.. code-block:: python

	class MySnippetPlugin(ShopPluginBase):
	    ...
	    glossary_fields = (
	        PartialFormField('title',
	            widgets.TextInput(),
	            label=_("Title")
	        ),
	    )

Inside the rendering template for that plugin, the newly added title can be accessed as:

.. code-block:: django

	<h1>{{ instance.glossary.title }}</h1>
	<div>...

**Cascade** offers many more options than just these. For details please check its
`reference guide`_.


.. _encapsulation: https://en.wikipedia.org/wiki/Encapsulation_(computer_programming)
.. _django-sekizai: http://django-sekizai.readthedocs.org/en/stable/
.. _reference guide: http://djangocms-cascade.readthedocs.org/en/stable/
