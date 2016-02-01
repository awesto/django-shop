# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.conf import settings
from django.contrib.staticfiles.finders import (FileSystemFinder as FileSystemFinderBase,
        AppDirectoriesFinder as AppDirectoriesFinderBase)


class FileSystemFinder(FileSystemFinderBase):
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
                unminimized_path = super(FileSystemFinder, self).find_location(root, base + ext, prefix)
                if unminimized_path:
                    return unminimized_path
        # otherwise proceed with the given one
        path = super(FileSystemFinder, self).find_location(root, path, prefix)
        return path


class AppDirectoriesFinder(AppDirectoriesFinderBase):
    serve_unminimized = getattr(settings, 'DEBUG', False)

    def find_in_app(self, app, path):
        matched_path = super(AppDirectoriesFinder, self).find_in_app(app, path)
        if matched_path and self.serve_unminimized:
            base, ext = os.path.splitext(matched_path)
            base, minext = os.path.splitext(base)
            if minext == '.min':
                storage = self.storages.get(app, None)
                path = '{}{}'.format(base, ext)
                if storage.exists(path):
                    path = storage.path(path)
                    if path:
                        return path
        return matched_path
