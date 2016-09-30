# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import requests
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves import input
try:
    import czipfile as zipfile
except ImportError:
    import zipfile


class Command(BaseCommand):
    help = _("Initialize the workdir to run the demo of myshop.")
    download_url = 'http://downloads.django-shop.org/django-shop-workdir_{tutorial}-{version}.zip'
    version = '0.9.2'
    pwd = b'z7xv'

    def add_arguments(self, parser):
        parser.add_argument('--noinput', '--no-input',
            action='store_false', dest='interactive', default=True,
            help="Do NOT prompt the user for input of any kind.")

    def set_options(self, **options):
        self.interactive = options['interactive']

    def handle(self, verbosity, *args, **options):
        self.set_options(**options)

        mesg = ("\nThis will overwrite your workdir and install a new database for the djangoSHOP demo: {tutorial}\n"
                "Are you sure you want to do this?\n\n"
                "Type 'yes' to continue, or 'no' to cancel: ").format(tutorial=settings.SHOP_TUTORIAL)
        if self.interactive and input(mesg) != 'yes':
            raise CommandError("Collecting static files cancelled.")

        extract_to = os.path.join(settings.WORK_DIR, os.pardir)
        msg = "Downloading workdir and extracting to {}. Please wait ..."
        self.stdout.write(msg.format(extract_to))
        download_url = self.download_url.format(tutorial=settings.SHOP_TUTORIAL, version=self.version)
        response = requests.get(download_url, stream=True)
        zip_ref = zipfile.ZipFile(StringIO(response.content))
        try:
            zip_ref.extractall(extract_to, pwd=self.pwd)
        finally:
            zip_ref.close()

        call_command('migrate')
        fixture = '{workdir}/{tutorial}/fixtures/myshop.json'
        call_command('loaddata', fixture.format(workdir=settings.WORK_DIR,
                                                tutorial=settings.SHOP_TUTORIAL))
