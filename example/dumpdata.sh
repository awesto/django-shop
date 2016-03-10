#!/bin/sh
./manage.py dumpdata --indent=2 --natural-foreign email_auth cms cmsplugin_cascade djangocms_text_ckeditor filer shop myshop --exclude cmsplugin_cascade.segmentation --exclude filer.clipboard --exclude filer.clipboarditem > fixtures/myshop-$DJANGO_SHOP_TUTORIAL.json
