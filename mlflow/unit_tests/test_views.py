import json
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase
from pandas import DataFrame

from mlflow.forms import DataFileForm, ControlPanelForm
from mlflow.views import home_view, train_model, load_file


class HomeViewTestCase(SimpleTestCase):
    json_data = {
        "Col1": {"0": 1.0, "1": 2, "2": 3, "3": 4, "4": 5},
        "Col2": {"0": 5.0, "1": 6, "2": 7, "3": 8, "4": 9}
    }

    @patch("mlflow.views.render")
    def test_home_view_returns_initialized_forms(self, mock_render):
        mock_request = "GET"
        home_view(mock_request)
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][0], "GET")
        self.assertEqual(mock_render.call_args[0][1], "home.html")
        self.assertEqual(mock_render.call_args[0][2]['error_message'], None)
        self.assertEqual(type(mock_render.call_args[0][2]['datafile_form']), DataFileForm)
        self.assertEqual(type(mock_render.call_args[0][2]['control_form']), ControlPanelForm)

    @patch("mlflow.views.read_csv_datafile")
    def test_load_file_returns_file_data_info(self, mock_reader):
        mock_request = MagicMock()
        mock_request.GET = {"data_file": "file.dat"}
        mock_reader.return_value = DataFrame(self.json_data)
        response = load_file(mock_request)
        response = json.loads(response.content)
        self.assertEqual(response['error_message'], None)
        self.assertEqual(response['file_name'], 'file.dat')
        self.assertEqual(response['target_feature'], 'Col2')
        self.assertEqual(len(response['column_summary']), 2)
        self.assertTrue(response['data_frame'] is not None)


    @patch("mlflow.views.fit_linear_regression")
    def test_train_model_handles_exception(self, mock_fit):
        mock_request = _setup_mock_request(self.json_data)
        mock_fit.side_effect = Exception("Error occurred")
        json_response = train_model(mock_request)
        self.assertJSONEqual(json_response.content, {"error_message": "Error occurred"})
        mock_fit.assert_called_once_with(self.json_data, 3)

    @patch("mlflow.views.fit_linear_regression")
    def test_train_model_returns_fit_results(self, mock_fit):
        mock_request = _setup_mock_request(self.json_data)
        mock_fit.return_value = {"n_splits": 5}
        json_response = train_model(mock_request)
        mock_fit.assert_called_once_with(self.json_data, 3)
        self.assertJSONEqual(json_response.content, {"error_message": "None", "n_splits": 5})


def _setup_mock_request(json_data):
    mock_request = MagicMock()
    mock_request.GET = {"n_splits": "3", "datafile": "file.dat"}
    mock_request.session = {"data_frame": json_data}
    return mock_request
