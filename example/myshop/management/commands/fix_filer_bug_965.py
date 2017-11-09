# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from filer.models.imagemodels import Image


class Command(BaseCommand):
    help = _("Fix https://github.com/divio/django-filer/issues/965")

    def handle(self, verbosity, *args, **options):
        for img in Image.objects.all():
            img.file_data_changed()
            img.save()
