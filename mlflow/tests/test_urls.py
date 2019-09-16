from django.test import SimpleTestCase
from django.urls import reverse, resolve
from mlflow.views import home_view


class UrlsTestCase(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, home_view)
        url = reverse('home')
        self.assertEquals(resolve(url).func, home_view)
