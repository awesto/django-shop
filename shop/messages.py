# -*- coding: utf-8 -*-
"""
A wrapper around Django's messages framework for easier integration with Javascript based messages.
"""
from __future__ import unicode_literals

import json
from django.contrib import messages as django_messages
from django.utils.text import force_text


def add_message(request, level, message, title=None, delay=None):
    if title is None:
        title = django_messages.DEFAULT_TAGS[level].capitalize()
    extra_tags = {'title': force_text(title), 'delay': delay}
    django_messages.add_message(request, level, force_text(message), extra_tags=json.dumps(extra_tags))


def success(request, message, title=None, delay=0):
    add_message(request, django_messages.SUCCESS, message, title, delay)


def warning(request, message, title=None, delay=0):
    add_message(request, django_messages.WARNING, message, title, delay)


def error(request, message, title=None, delay=0):
    add_message(request, django_messages.ERROR, message, title, delay)


def info(request, message, title=None, delay=0):
    add_message(request, django_messages.INFO, message, title, delay)


def debug(request, message, title=None, delay=0):
    add_message(request, django_messages.DEBUG, message, title, delay)


def get_messages_as_json(request):
    data = []
    for message in django_messages.get_messages(request):
        try:
            extra_tags = json.loads(message.extra_tags)
        except (TypeError, json.JSONDecodeError):
            extra_tags = {}
        heading = extra_tags.get('title', message.level_tag.capitalize())
        try:
            delay = int(float(extra_tags['delay']) * 1000)
        except (KeyError, ValueError):
            delay = None
        data.append({
            'level': message.level_tag,
            'heading': heading,
            'body': message.message,
            'delay': delay,
        })
    return data
