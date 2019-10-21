from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase

from mlflow.views import home_view, train_model


def _setup_mock_request(json_data):
    mock_request = MagicMock()
    mock_request.GET = {"training_ratio": "0.7", "datafile": "file.dat"}
    mock_request.session = {"dataframe": json_data}
    return mock_request


class HomeViewTestCase(SimpleTestCase):

    json_data = {"Col1":{"0":1,"1":2,"2":3,"3":4,"4":5},"Col2":{"0":5,"1":6,"2":7,"3":8,"4":9}}

    @patch("mlflow.views.get_context")
    @patch("mlflow.views.render")
    def test_home_view_calls_get_context_with_request(self, mock_render, mock_get_context):
        mock_request = "GET"
        mock_context = {"data": 1234}
        mock_get_context.return_value = mock_context
        mock_render.return_value = "html response"
        response = home_view(mock_request)
        mock_get_context.assert_called_once_with(mock_request)
        mock_render.assert_called_once_with(mock_request, 'home.html', mock_context)
        self.assertEqual(response, "html response")

    @patch("mlflow.views.fit_linear_regression")
    def test_train_model_handles_exception(self, mock_fit):
        mock_request = _setup_mock_request(self.json_data)
        mock_fit.side_effect = Exception("Error occurred")
        json_response = train_model(mock_request)
        self.assertJSONEqual(json_response.content, {"error_message": "Error occurred"})
        mock_fit.assert_called_once_with(self.json_data, 0.7)

    @patch("mlflow.views.fit_linear_regression")
    def test_train_model_returns_fit_results(self, mock_fit):
        mock_request = _setup_mock_request(self.json_data)
        mock_fit.return_value = {"train_score": 0.8}
        json_response = train_model(mock_request)
        mock_fit.assert_called_once_with(self.json_data, 0.7)
        self.assertJSONEqual(json_response.content, {"error_message": "None", "train_score": 0.8})

