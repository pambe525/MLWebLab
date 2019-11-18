import json
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase
from pandas import DataFrame, read_json

from mlflow.forms import DataFileForm, ControlPanelForm
from mlflow.views import home_view, train_model, load_file


class HomeViewTestCase(SimpleTestCase):
    json_data = {
        "Col1": {"0": 1, "1": 2, "2": 3, "3": 4, "4": 5},
        "Col2": {"0": 5, "1": 6, "2": 7, "3": 8, "4": 9}
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
        mock_request = _setup_mock_request()
        mock_reader.return_value = DataFrame(self.json_data)
        response = load_file(mock_request)
        response = json.loads(response.content)
        self.assertEqual(response['error_message'], None)
        self.assertEqual(response['file_name'], 'file.dat')
        self.assertEqual(response['target_feature'], 'Col2')
        self.assertEqual(len(response['column_summary']), 2)
        self.assertTrue(response['data_frame'] is not None)

    @patch("mlflow.views.read_csv_datafile")
    def test_load_file_returns_correlation_matrix(self, mock_reader):
        mock_request = _setup_mock_request()
        mock_reader.return_value = DataFrame(self.json_data)
        response = load_file(mock_request)
        response = json.loads(response.content)
        self.assertTrue(isinstance(response['correlation_matrix'], list))
        self.assertEqual(len(response['correlation_matrix']), 2)

    @patch("mlflow.views.read_csv_datafile")
    def test_load_file_saves_data_frame_to_session(self, mock_reader):
        mock_request = _setup_mock_request()
        data_frame = DataFrame(self.json_data)
        mock_reader.return_value = data_frame
        load_file(mock_request)
        self.assertEqual(mock_request.session["data_frame"], data_frame.to_json())

    @patch("mlflow.views.fit_linear_regression")
    def test_train_model_handles_exception(self, mock_fit):
        mock_request = _setup_mock_request(json_data=self.json_data)
        mock_fit.side_effect = Exception("Error occurred")
        json_response = train_model(mock_request)
        mock_fit.assert_called_once()
        self.assertJSONEqual(json_response.content, {"error_message": "Error occurred"})

    @patch("mlflow.views.fit_linear_regression")
    def test_train_model_returns_fit_results(self, mock_fit):
        mock_request = _setup_mock_request(json_data=self.json_data)
        mock_fit.return_value = {"score": 2.3}
        json_response = train_model(mock_request)
        mock_fit.assert_called_once()
        data_frame = DataFrame(self.json_data)
        self.assertEqual(mock_fit.call_args[0][0].to_json(), data_frame.to_json())
        self.assertEqual(mock_fit.call_args[0][1], 3)
        self.assertJSONEqual(json_response.content, {"error_message": None, "score": 2.3})


def _setup_mock_request(json_data=None):
    mock_request = MagicMock()
    mock_request.GET = {"n_splits": "3", "data_file": "file.dat"}
    mock_request.session = {} if json_data is None else {"data_frame": json.dumps(json_data)}
    return mock_request
