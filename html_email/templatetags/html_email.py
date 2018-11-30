# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from email.mime.image import MIMEImage
from django import template
from django.contrib.staticfiles import finders
from django.core.files import File
from django.core.files.images import ImageFile

register = template.Library()


@register.simple_tag(takes_context=True)
def image_src(context, file):
    if isinstance(file, ImageFile):
        fileobj = file
    else:
        absfilename = finders.find(file)
        if absfilename is None:
            raise FileNotFoundError("No such file: {}".format(file))
        fileobj = File(open(absfilename, 'rb'), name=file)
    image = MIMEImage(fileobj.read())
    image.add_header('Content-Disposition', 'inline', filename=fileobj.name)
    image.add_header('Content-ID', '<{}>'.format(fileobj.name))
    context.template._attached_images.append(image)
    return 'cid:{}'.format(fileobj.name)
