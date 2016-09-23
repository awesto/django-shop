# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import StringIO
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _
try:
    import czipfile as zipfile
except ImportError:
    import zipfile


class Command(BaseCommand):
    help = _("Initialize the workdir to run the demo of myshop.")
    download_url = 'http://downloads.django-shop.org/django-shop-workdir-0.9.2.zip'
    pwd = 'z7xv'

    def handle(self, verbosity, *args, **options):
        msg = "Downloading workdir. Please wait, this may take a few minutes."
        self.stdout.write(msg)
        response = requests.get(self.download_url, stream=True)
        try:
            zip_ref = zipfile.ZipFile(StringIO.StringIO(response.content))
            zip_ref.extractall(settings.PROJECT_ROOT, pwd=self.pwd)
        finally:
            zip_ref.close()
