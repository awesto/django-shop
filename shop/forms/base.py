# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from formtools.wizard.views import normalize_name
from django.forms import fields
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from cms.utils.helpers import classproperty
from djng.forms import NgModelFormMixin, NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3ModelForm


class DialogFormMixin(NgModelFormMixin, NgFormValidationMixin):
    required_css_class = 'djng-field-required'

    def __init__(self, *args, **kwargs):
        kwargs.pop('cart', None)  # cart object must be removed, otherwise underlying methods complain
        super(DialogFormMixin, self).__init__(*args, **kwargs)

    @classproperty
    def form_name(cls):
        return normalize_name(cls.__name__)

    def clean(self):
        cleaned_data = dict(super(DialogFormMixin, self).clean())
        cleaned_data.pop('plugin_id')
        cleaned_data.pop('plugin_order')
        return cleaned_data

    def as_text(self):
        """
        Dialog Forms rendered as summary just display their values instead of input fields.
        This is useful to render a summary of a previously filled out form.
        """
        output = []
        for name in self.fields.keys():
            bound_field = self[name]
            value = bound_field.value()
            if bound_field.is_hidden:
                continue
            if isinstance(value, (list, tuple)):
                line = []
                cast_to = type(tuple(bound_field.field.choices)[0][0])
                for v in value:
                    try:
                        line.append(dict(bound_field.field.choices)[cast_to(v)])
                    except (AttributeError, KeyError):
                        pass
                output.append(force_text(', '.join(line)))
            elif value:
                try:
                    value = dict(bound_field.field.choices)[value]
                except (AttributeError, KeyError):
                    pass
                output.append(force_text(value))
        return mark_safe('\n'.join(output))

    def get_response_data(self):
        """
        Hook to respond with an updated version of the form data. This response then merged
        into the scope by dialogs.js
        """


class DialogForm(DialogFormMixin, Bootstrap3Form):
    """
    Base class for all dialog forms used with a DialogFormPlugin.
    """
    plugin_id = fields.CharField(widget=fields.HiddenInput)
    plugin_order = fields.CharField(widget=fields.HiddenInput)


class DialogModelForm(DialogFormMixin, Bootstrap3ModelForm):
    """
    Base class for all dialog model forms used with a DialogFormPlugin.
    """
    plugin_id = fields.CharField(widget=fields.HiddenInput)
    plugin_order = fields.CharField(widget=fields.HiddenInput)
