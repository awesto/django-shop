from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.backends.base import BaseEngine
from django.template.backends.django import Template as DjangoTemplate, reraise, get_installed_libraries
from django.template.engine import Engine


class Template(DjangoTemplate):
    def attach_images(self, email_message):
        assert isinstance(email_message, EmailMultiAlternatives), "Parameter must be of type EmailMultiAlternatives"
        for attachment in self.template._attached_images:
            email_message.attach(attachment)


class EmailTemplates(BaseEngine):
    """
    Customized Template Engine which keeps track on referenced images and stores then as attachments
    to be used in multipart email messages.
    """
    app_dirname = 'templates'

    def __init__(self, params):
        params = params.copy()
        options = params.pop('OPTIONS').copy()
        options.setdefault('autoescape', True)
        options.setdefault('debug', settings.DEBUG)
        options.setdefault('file_charset', settings.FILE_CHARSET)
        libraries = options.get('libraries', {})
        options['libraries'] = self.get_templatetag_libraries(libraries)
        super(EmailTemplates, self).__init__(params)
        self.engine = Engine(self.dirs, self.app_dirs, **options)

    def from_string(self, template_code):
        return Template(self.engine.from_string(template_code), self)

    def get_template(self, template_name):
        try:
            template = self.engine.get_template(template_name)
            template._attached_images = []
            return Template(template, self)
        except TemplateDoesNotExist as exc:
            reraise(exc, self)

    def get_templatetag_libraries(self, custom_libraries):
        libraries = get_installed_libraries()
        libraries.update(custom_libraries)
        return libraries
