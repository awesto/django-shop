from django.forms import fields, widgets
from django.utils.translation import gettext_lazy as _, ngettext_lazy
from django.utils.text import Truncator
from django.utils.html import format_html
from django.forms.fields import IntegerField
from django.template.loader import select_template
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.widgets import NumberInputWidget
from cmsplugin_cascade.plugin_base import TransparentWrapper, TransparentContainer
from shop.conf import app_settings
from shop.cascade.plugin_base import ShopPluginBase


class ProcessBarFormMixin(ManageChildrenFormMixin, EntangledModelFormMixin):
    num_children = IntegerField(
        min_value=1,
        initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em;'}),
        label=_("Steps"),
        help_text=_("Number of steps for this proceed bar."))

    class Meta:
        untangled_fields = ['num_children']


class ProcessBarPlugin(TransparentWrapper, ShopPluginBase):
    name = _("Process Bar")
    form = ProcessBarFormMixin
    parent_classes = ('BootstrapColumnPlugin',)
    direct_child_classes = ('ProcessStepPlugin',)
    require_parent = True
    allow_children = True

    @classmethod
    def get_identifier(cls, instance):
        identifier = super().get_identifier(instance)
        num_cols = instance.get_children().count()
        content = ngettext_lazy('with {} page', 'with {} pages', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/process-bar.html'.format(app_settings.APP_LABEL),
            'shop/checkout/process-bar.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        self.super(ProcessBarPlugin, self).render(context, instance, placeholder)
        num_children = instance.get_num_children()
        if num_children > 0:
            context['step_css_width'] = '{:3.2f}%'.format(100. / num_children)
        return context

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super().save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, ProcessStepPlugin)

plugin_pool.register_plugin(ProcessBarPlugin)


class ProcessStepFormMixin(EntangledModelFormMixin):
    step_title = fields.CharField(
        widget=widgets.TextInput(attrs={'size': 50}),
        label=_("Step Title"),
        required=False,
    )

    class Meta:
        entangled_fields = {'glossary': ['step_title']}


class ProcessStepPlugin(TransparentContainer, ShopPluginBase):
    name = _("Process Step")
    direct_parent_classes = parent_classes = ['ProcessBarPlugin']
    require_parent = True
    allow_children = True
    alien_child_classes = True
    form = ProcessStepFormMixin
    render_template = 'cascade/generic/wrapper.html'

    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        content = obj.glossary.get('step_title', '')
        if content:
            content = Truncator(content).words(3, truncate=' ...')
        else:
            content = obj.get_position_in_placeholder()
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(ProcessStepPlugin)
