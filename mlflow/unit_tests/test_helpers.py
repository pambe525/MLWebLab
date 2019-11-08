import os
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from pandas import DataFrame
from pandas.errors import EmptyDataError

from mlflow import constants
from mlflow.forms import ControlPanelForm
from mlflow.helpers import dataframe_has_headers
from mlflow.helpers import get_context
from mlflow.helpers import read_csv_datafile
from mlflow.helpers import set_control_panel_context
from mlflow.helpers import set_file_selection_context


class HelperStaticFunctionsTestCase(SimpleTestCase):
    mock_data = data = {"Col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "Col3": [9, 10, 11, 12],
                        "Col4": [13, 14, 15, 16], "Col5": [17, 18, 19, 20]}
    mock_data_summary = [{"name": "Col1", "type": "int64", "min": 1, "max": 4, "mean": 2.5, "stdev": 1.29},
                         {"name": "col2", "type": "int64", "min": 5, "max": 8, "mean": 6.5, "stdev": 1.29},
                         {"name": "Col3", "type": "int64", "min": 9, "max": 12, "mean": 10.5, "stdev": 1.29},
                         {"name": "Col4", "type": "int64", "min": 13, "max": 16, "mean": 14.5, "stdev": 1.29},
                         {"name": "Col5", "type": "int64", "min": 17, "max": 20, "mean": 18.5, "stdev": 1.29}]

    def test_set_file_selection_context_as_enabled(self):
        context = {}
        form = MagicMock()
        context = set_file_selection_context(context, form, True)
        self.assertEqual(context["datafile_form"], form)

    def test_set_file_selection_context_as_disabled(self):
        context = {}
        form = MagicMock()
        context = set_file_selection_context(context, form, False)
        self.assertEqual(context["datafile_form"], form)

    def test_dataframe_has_headers_with_proper_headers(self):
        data = {"Col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "Col3": [9, 10, 11, 12],
                "Col4": [13, 14, 15, 16], "Col5": [17, 18, 19, 20]}
        self.assertTrue(dataframe_has_headers(DataFrame(data)))

    def test_dataframe_has_headers_with_mixed_headers(self):
        data = {"1.2": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "2": [9, 10, 11, 12],
                "Col4": [13, 14, 15, 16], 3: [17, 18, 19, 20]}
        self.assertFalse(dataframe_has_headers(DataFrame(data)))

    def test_dataframe_has_headers_with_numeric_headers(self):
        data = {"1": [1, 2, 3, 4], "2.0": [5, 6, 7, 8], "3": [9, 10, 11, 12],
                "4": [13, 14, 15, 16], "5": [17, 18, 19, 20]}
        self.assertFalse(dataframe_has_headers(DataFrame(data)))

    def test_set_default_container_context(self):
        data = {"Col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "Col3": [9, 10, 11, 12],
                "Col4": [13, 14, 15, 16], "Col5": [17, 18, 19, 20]}
        context = {}
        filename = "somefile.dat"
        data_frame = DataFrame(data)
        form = ControlPanelForm()
        context = set_control_panel_context(context, form, filename, data_frame)
        self.assertEqual(context['control_form'], form)
        self._verify_container_content(context, filename, data_frame)

    def test_read_csv_data_file(self):
        data = {"col1": list(range(10)), "col2": list(range(10, 20)), "col3": list(range(20, 30)),
                "col4": list(range(30, 40)), "col5": list(range(40,50))}
        filename = "test.csv"
        filepath = os.path.join(constants.DATA_FILE_PATH, filename)
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            dataframe = read_csv_datafile(filename)
            mock_read_csv.assert_called_once_with(filepath)
        self.assertEqual(dataframe.shape[0], 10)
        self.assertEqual(dataframe.shape[1], 5)

    def test_read_csv_data_file_with_read_exception(self):
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.side_effect = EmptyDataError("No data in file")
            try:
                read_csv_datafile("test.csv")
            except EmptyDataError as e:
                mock_read_csv.assert_called_once()
                self.assertEqual(str(e), "No data in file")

    def test_read_csv_data_file_with_one_column_in_data_file_error(self):
        data = {"col1": [1, 2, 3, 4]}
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            try:
                read_csv_datafile("test.csv")
            except Exception as e:
                mock_read_csv.assert_called_once()
                self.assertTrue("Data file has only one column" in str(e))

    def test_read_csv_data_file_with_numeric_headers_error(self):
        data = {"1.5": [1.1, 2.1, 3.1], "2.2": [1.2, 2.2, 3.2], "col3": [1.3, 2.3, 3.3]}
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            try:
                read_csv_datafile("test.csv")
            except Exception as e:
                mock_read_csv.assert_called_once()
                self.assertTrue("Data file has no headers" in str(e))

    def test_read_csv_data_file_with_less_than_10_records(self):
        data = {"col1": list(range(9)), "col2": list(range(10, 19)), "col3": list(range(20, 29)),
                "col4": list(range(30, 39)), "col5": list(range(40, 49))}
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            try:
                read_csv_datafile("test.csv")
            except Exception as e:
                mock_read_csv.assert_called_once()
                self.assertTrue("Data file has fewer than 10 records" in str(e))

    def test_get_context_with_GET_response_loads_file_list(self):
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices, mock_request = self._setup_mocks(mock_csv_read, mock_datafile_list, "GET")
                context = get_context(mock_request)
                mock_datafile_list.assert_called_once()
                mock_csv_read.assert_not_called()
                self._verify_file_selection_form(context, "GET", len(file_choices))

    def test_get_context_with_SELECT_button_and_no_file_selected(self):
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices, mock_request = self._setup_mocks(mock_csv_read, mock_datafile_list, "POST")
                mock_request.POST = {"data_file": constants.FILE_SELECT_DEFAULT}
                context = get_context(mock_request)
                self._verify_file_selection_form(context, "POST", len(file_choices))

    def test_get_context_with_SELECT_button_and_file_selected(self):
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices, mock_request = self._setup_mocks(mock_csv_read, mock_datafile_list, "POST")
                mock_request.POST = {"data_file": "a2.txt"}
                mock_request.session = {"datafile": None, "dataframe": None}
                context = get_context(mock_request)
                mock_csv_read.assert_called_once()
                self._verify_file_selection_form(context, "POST", len(file_choices), selected_file="a2.txt")
                self._verify_container_content(context, "a2.txt", mock_csv_read.return_value)
                self._verify_validation_content(context, False)
                self._verify_features_summary(context, self.mock_data_summary)
                self._verify_dataframe_values(context, self.mock_data)
                # Verify session variables are saved
                json_dataframe = mock_csv_read.return_value.to_json()
                self.assertEqual(mock_request.session['datafile'], "a2.txt")
                self.assertEqual(mock_request.session['dataframe'], json_dataframe)

    def test_get_context_with_SELECT_button_and_read_exception(self):
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices, mock_request = self._setup_mocks(mock_csv_read, mock_datafile_list, "POST")
                mock_request.POST = {"data_file": "a2.txt"}
                mock_csv_read.side_effect = Exception("Error occurred")
                with self.assertRaises(Exception) as raised:
                    context = get_context(mock_request)
                    self.assertTrue("Error occurred" in str(raised.exception))
                    self._verify_file_selection_form(context, "POST", len(file_choices), selected_file="a2.txt")

    # ------------------------------------------------------------------------------------------------------------------
    def _setup_mocks(self, mock_csv_read, mock_datafile_list, method):
        file_choices = [(constants.FILE_SELECT_DEFAULT, constants.FILE_SELECT_DEFAULT), ("a1.txt", "a1.txt"),
                        ("a2.txt", "a2.txt")]
        mock_datafile_list.return_value = file_choices
        mock_csv_read.return_value = DataFrame(self.mock_data)
        mock_request = MagicMock()
        mock_request.method = method
        return file_choices, mock_request

    def _verify_file_selection_form(self, context, response_method, n_files, selected_file=constants.FILE_SELECT_DEFAULT):
        form = context['datafile_form']
        if response_method == "GET":
            self.assertFalse(form.is_valid())
            self.assertFalse(form.is_bound)
            self.assertEqual(form.fields['data_file'].initial, constants.FILE_SELECT_DEFAULT)
            self.assertEqual(len(form.fields['data_file'].choices), n_files)
        elif response_method == "POST" and selected_file == constants.FILE_SELECT_DEFAULT:
            self.assertFalse(form.is_valid())
            self.assertTrue(form.is_bound)
            self.assertEqual(form.fields['data_file'].initial, constants.FILE_SELECT_DEFAULT)
            self.assertEqual(len(form.fields['data_file'].choices), n_files)
        else:
            self.assertTrue(form.is_bound)
            self.assertEqual(form.fields['data_file'].initial, selected_file)

    def _verify_container_content(self, context, filename, dataframe):
        self.assertEqual(context['data_file_name'], filename)
        self.assertEqual(context['data_file_rows'], dataframe.shape[0])
        self.assertEqual(context['data_file_cols'], dataframe.shape[1])
        self.assertEqual(context['target_feature'], dataframe.columns[-1])

    def _verify_features_summary(self, context, stat_table):
        self.assertEqual(context['features_summary'], stat_table)

    def _verify_dataframe_values(self, context, data_table):
        self.assertEqual(context['data_frame'], DataFrame(data_table).to_json())

    def _verify_validation_content(self, context, is_enabled):
        if not is_enabled:
            self.assertEqual(context['active_tab'], "data_summary")
        else:
            self.assertEqual(context['active_tab'], "train")
            self.assertEqual(context['training_method'], "Linear Regression")
            self.assertGreater(float(context['validation_score']), 0)
            self.assertGreater(float(context['training_score']), 0)
