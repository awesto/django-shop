# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder


class ServeUnminimizedFinder(FileSystemFinder):
    """
    In debug mode, serve /static/any/asset.min.ext as /static/any/asset.ext
    """
    locations = []
    serve_unminimized = getattr(settings, 'DEBUG', False)

    def find_location(self, root, path, prefix=None):
        if self.serve_unminimized:
            # search for the unminimized version, and if it exists, return it
            base, ext = os.path.splitext(path)
            base, minext = os.path.splitext(base)
            if minext == '.min':
                unminimized_path = super(ServeUnminimizedFinder, self).find_location(root, base + ext, prefix)
                if unminimized_path:
                    return unminimized_path
        # otherwise proceed with the given one
        path = super(ServeUnminimizedFinder, self).find_location(root, path, prefix)
        return path
