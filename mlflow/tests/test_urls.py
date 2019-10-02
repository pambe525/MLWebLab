from django.test import SimpleTestCase
from django.urls import reverse, resolve
from mlflow.views import home_view, datafile_selected, train_model


class UrlsTestCase(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, home_view)

    def test_datafile_selected_is_resolved(self):
        url = reverse('datafile_selected')
        self.assertEquals(resolve(url).func, datafile_selected)

    def test_train_model_is_resolved(self):
        url = reverse('train_model')
        self.assertEquals(resolve(url).func, train_model)