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
    download_url = 'http://downloads.django-shop.org/django-shop-workdir_{tutorial}-{version}.zip'
    version = '0.9.2'
    pwd = 'z7xv'

    def handle(self, verbosity, *args, **options):
        msg = "Downloading and extracting workdir. Please wait ..."
        self.stdout.write(msg)
        download_url = self.download_url.format(tutorial=settings.SHOP_TUTORIAL, version=self.version)
        response = requests.get(download_url, stream=True)
        try:
            zip_ref = zipfile.ZipFile(StringIO.StringIO(response.content))
            zip_ref.extractall(settings.PROJECT_ROOT, pwd=self.pwd)
        finally:
            zip_ref.close()
