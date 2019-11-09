from django.test import SimpleTestCase
from django.urls import reverse, resolve

from mlflow.views import home_view, train_model, load_file


class UrlsTestCase(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, home_view)

    def test_load_file_url_is_resolved(self):
        url = reverse('load_file')
        self.assertEquals(resolve(url).func, load_file)

    def test_train_model_url_is_resolved(self):
        url = reverse('train_model')
        self.assertEquals(resolve(url).func, train_model)