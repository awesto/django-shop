# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from .notification import Notification, NotificationAttachment

if getattr(settings, 'AUTH_USER_MODEL', None) == 'shop.User':
    from .auth import User
