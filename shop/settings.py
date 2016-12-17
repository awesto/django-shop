# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from shop import app_settings

import sys  # noqa
settings = app_settings.__class__()
settings.__name__ = __name__
sys.modules[__name__] = settings
