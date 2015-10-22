from django.test import TestCase

import mock

from rest_framework.test import APIRequestFactory

from shop.rest.auth import PasswordResetSerializer


class PasswordResetSerializerTest(TestCase):

    def test_save(self):
        data = {'email': 'test@example.org'}
        request = APIRequestFactory().post('/', data)
        serializer = PasswordResetSerializer(data=data, context={
            'request': request,
        })
        self.assertTrue(serializer.is_valid())
        serializer.reset_form = mock.Mock()
        serializer.save()
        serializer.reset_form.save.assert_called_with(
            use_https=False,
            from_email='webmaster@localhost',
            request=request,
            subject_template_name=u'shop/email/reset-password-subject.txt',
            email_template_name='shop/email/reset-password-body.txt',
        )
