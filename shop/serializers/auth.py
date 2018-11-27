from __future__ import unicode_literals

from rest_auth.serializers import LoginSerializer as DefaultLoginSerializer
from rest_framework import serializers


class LoginSerializer(DefaultLoginSerializer):
    stay_logged_in = serializers.BooleanField(required=False)
