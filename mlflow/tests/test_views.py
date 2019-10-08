from django.test import SimpleTestCase
from unittest.mock import patch
from mlflow.views import home_view


class HomeViewTestCase(SimpleTestCase):

    def test_home_view_calls_get_context_with_request(self):
        with patch("mlflow.views.get_context") as mock_get_context:
            with patch("mlflow.views.render") as mock_render:
                mock_request = "GET"
                mock_context = {"data": 1234}
                mock_get_context.return_value = mock_context
                mock_render.return_value = "html response"
                response = home_view(mock_request)
                mock_get_context.assert_called_once_with(mock_request)
                mock_render.assert_called_once_with(mock_request, 'home.html', mock_context)
                self.assertEqual(response, "html response")
