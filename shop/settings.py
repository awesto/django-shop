# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from shop import app_settings


# Change the export value of the module, to allow importing with `from shop import settings`
# For more details, see http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys  # noqa
settings = app_settings.__class__()
settings.__name__ = __name__
sys.modules[__name__] = settings
