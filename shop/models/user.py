# -*- coding: utf-8 -*-
from django.conf import settings

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
