from django.test import SimpleTestCase, Client
from django.urls import reverse
from mlflow.views import home_view

class HomeViewTestCase(SimpleTestCase):

    def test_home_view_return_proper_context(self):
        client = Client()
        response = client.get(reverse("home"))
        self.assertEquals(response.context['visibility'], 'invisible', 'Flow panel visibility')
        self.assertGreater(len(response.context['filenames']), 5, 'Has some filenames')
        self.assertTrue("ex1data1.txt" in response.context['filenames'], 'Check one filename')
