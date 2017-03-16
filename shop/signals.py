# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.dispatch import Signal


customer_recognized = Signal(providing_args=['customer', 'request'])
