from django.test import TestCase


class StartpageTest(TestCase):

    def test_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)
