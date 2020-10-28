from formtools.wizard.views import normalize_name

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cms.utils.helpers import classproperty

from djng.forms import fields, NgModelFormMixin, NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3ModelForm


class DialogFormMixin(NgModelFormMixin, NgFormValidationMixin):
    required_css_class = 'djng-field-required'

    def __init__(self, *args, **kwargs):
        kwargs.pop('cart', None)  # cart object must be removed, otherwise underlying methods complain
        auto_name = self.form_name  ## .replace('_form', '')
        kwargs.setdefault('auto_id', '{}-%s'.format(auto_name))
        super().__init__(*args, **kwargs)

    @classproperty
    def form_name(cls):
        return normalize_name(cls.__name__)

    def clean(self):
        cleaned_data = dict(super().clean())
        cleaned_data.pop('plugin_id', None)
        if cleaned_data.pop('plugin_order', None) is None:
            msg = "Field 'plugin_order' is a hidden but required field in each form inheriting from DialogFormMixin"
            raise ValidationError(msg)
        return cleaned_data

    def as_text(self):
        """
        Dialog Forms rendered as summary just display their values instead of input fields.
        This is useful to render a summary of a previously filled out form.
        """
        try:
            return mark_safe(self.instance.as_text())
        except (AttributeError, TypeError):
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
                    output.append(force_str(', '.join(line)))
                elif value:
                    try:
                        value = dict(bound_field.field.choices)[value]
                    except (AttributeError, KeyError):
                        pass
                    output.append(force_str(value))
            return mark_safe('\n'.join(output))

    def get_response_data(self):
        """
        Hook to respond with an updated version of the form data. This response then shall
        override the forms content.
        """


class DialogForm(DialogFormMixin, Bootstrap3Form):
    """
    Base class for all dialog forms used with a DialogFormPlugin.
    """
    label_css_classes = 'control-label font-weight-bold'

    plugin_id = fields.CharField(
        widget=widgets.HiddenInput,
        required=False,
    )

    plugin_order = fields.CharField(
        widget=widgets.HiddenInput,
    )


class DialogModelForm(DialogFormMixin, Bootstrap3ModelForm):
    """
    Base class for all dialog model forms used with a DialogFormPlugin.
    """
    plugin_id = fields.CharField(
        widget=widgets.HiddenInput,
        required=False,
    )

    plugin_order = fields.CharField(widget=widgets.HiddenInput)

    @cached_property
    def field_css_classes(self):
        css_classes = {'*': getattr(Bootstrap3ModelForm, 'field_css_classes')}
        for name, field in self.fields.items():
            if not field.widget.is_hidden:
                css_classes[name] = [css_classes['*']]
                css_classes[name].append('{}-{}'.format(self.scope_prefix, name))
        return css_classes


class UniqueEmailValidationMixin:
    """
    A mixin added to forms which have to validate for the uniqueness of email addresses.
    """
    def clean_email(self):
        if not self.cleaned_data['email']:
            raise ValidationError(_("Please provide a valid e-mail address"))
        # check for uniqueness of email address
        if get_user_model().objects.filter(is_active=True, email=self.cleaned_data['email']).exists():
            msg = _("A customer with the e-mail address '{email}' already exists.\n"
                    "If you have used this address previously, try to reset the password.")
            raise ValidationError(msg.format(**self.cleaned_data))
        return self.cleaned_data['email']
