import os
from django.test import SimpleTestCase
from unittest.mock import MagicMock, patch
from mlflow.helpers import set_file_selection_context
from mlflow.helpers import dataframe_has_headers
from mlflow.helpers import set_control_panel_context
from mlflow.helpers import get_context
from mlflow.helpers import read_csv_datafile
from django.conf import settings
from pandas import DataFrame
from pandas.errors import EmptyDataError
from mlflow.forms import ControlPanelForm
from mlflow.methods import fit_linear_regression


class HelperStaticFunctionsTestCase(SimpleTestCase):
    mock_data = data = {"Col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "Col3": [9, 10, 11, 12],
                        "Col4": [13, 14, 15, 16], "Col5": [17, 18, 19, 20]}

    def test_set_file_selection_context_as_enabled(self):
        context = {}
        form = MagicMock()
        context = set_file_selection_context(context, form, True)
        self.assertEqual(context["datafile_form"], form)
        self._verify_file_selection_enabled(context, True)

    def test_set_file_selection_context_as_disabled(self):
        context = {}
        form = MagicMock()
        context = set_file_selection_context(context, form, False)
        self.assertEqual(context["datafile_form"], form)
        self._verify_file_selection_enabled(context, False)

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
        data = {"col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "col3": [9, 10, 11, 12],
                "col4": [13, 14, 15, 16], "col5": [17, 18, 19, 20]}
        filename = "test.csv"
        filepath = os.path.join(settings.BASE_DIR, 'data/' + filename)
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            dataframe = read_csv_datafile(filename)
            mock_read_csv.assert_called_once_with(filepath)
        self.assertEqual(dataframe.shape[0], 4)
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
                self.assertEqual(str(e), "Data file has only one column")

    def test_read_csv_data_file_with_numeric_headers_error(self):
        data = {"1.5": [1.1, 2.1, 3.1], "2.2": [1.2, 2.2, 3.2], "col3": [1.3, 2.3, 3.3]}
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            try:
                read_csv_datafile("test.csv")
            except Exception as e:
                mock_read_csv.assert_called_once()
                self.assertEqual(str(e), "Data file has no headers")

    def test_get_context_with_GET_response_loads_file_list(self):
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices, mock_request = self._setup_mocks(mock_csv_read, mock_datafile_list, "GET")
                context = get_context(mock_request)
                mock_datafile_list.assert_called_once()
                mock_csv_read.assert_not_called()
                self._verify_file_selection_form(context, "GET", len(file_choices))
                self._verify_file_selection_enabled(context, True)

    def test_get_context_with_SELECT_button_and_no_file_selected(self):
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices, mock_request = self._setup_mocks(mock_csv_read, mock_datafile_list, "POST")
                mock_request.POST = {"data_file": "Choose a file..."}
                context = get_context(mock_request)
                self._verify_file_selection_form(context, "POST", len(file_choices))

    def test_get_context_with_SELECT_button_and_file_selected(self):
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices, mock_request = self._setup_mocks(mock_csv_read, mock_datafile_list, "POST")
                mock_request.POST = {"data_file": "a2.txt", "select_btn": []}
                mock_request.session = {"datafile": None, "dataframe": None}
                context = get_context(mock_request)
                mock_csv_read.assert_called_once()
                self._verify_file_selection_form(context, "POST", len(file_choices), selected_file="a2.txt")
                self._verify_file_selection_enabled(context, False)
                self._verify_container_content(context, "a2.txt", mock_csv_read.return_value)
                self._verify_validation_content(context, False)
                # Verify session variables are saved
                json_dataframe = mock_csv_read.return_value.to_json()
                self.assertEqual(mock_request.session['datafile'], "a2.txt")
                self.assertEqual(mock_request.session['dataframe'], json_dataframe)

    def test_get_context_with_SELECT_button_and_read_exception(self):
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices, mock_request = self._setup_mocks(mock_csv_read, mock_datafile_list, "POST")
                mock_request.POST = {"data_file": "a2.txt", "select_btn": []}
                mock_csv_read.side_effect = Exception("Error occurred")
                with self.assertRaises(Exception) as raised:
                    context = get_context(mock_request)
                    self.assertTrue("Error occurred" in str(raised.exception))
                    self._verify_file_selection_form(context, "POST", len(file_choices), selected_file="a2.txt")
                    self._verify_file_selection_enabled(context, True)

    def test_get_context_with_TRAIN_button_clicked(self):
        self.mock_data = {"X1": list(range(6)), "X2": list(reversed(range(6))), "y": list(range(15, 21))}
        print(self.mock_data)
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices, mock_request = self._setup_mocks(mock_csv_read, mock_datafile_list, "POST")
                mock_request.POST = {"training_method": "Linear Regression", "training_ratio": 0.8, "train_btn": []}
                json_data = DataFrame(self.mock_data).to_json()
                mock_request.session = {'datafile': "a2.txt", 'dataframe': json_data}
                context = get_context(mock_request)
                mock_csv_read.assert_not_called()
                self._verify_file_selection_form(context, "POST", len(file_choices), selected_file="a2.txt")
                self._verify_file_selection_enabled(context, False)
                self._verify_container_content(context, "a2.txt", DataFrame(self.mock_data))
                self._verify_validation_content(context, True)

    # ------------------------------------------------------------------------------------------------------------------
    def _setup_mocks(self, mock_csv_read, mock_datafile_list, method):
        file_choices = [("Choose a file...", "Choose a file..."), ("a1.txt", "a1.txt"),
                        ("a2.txt", "a2.txt")]
        mock_datafile_list.return_value = file_choices
        mock_csv_read.return_value = DataFrame(self.mock_data)
        mock_request = MagicMock()
        mock_request.method = method
        return file_choices, mock_request

    def _verify_file_selection_form(self, context, response_method, n_files, selected_file="Choose a file..."):
        form = context['datafile_form']
        if response_method == "GET":
            self.assertFalse(form.is_valid())
            self.assertFalse(form.is_bound)
            self.assertEqual(form.fields['data_file'].initial, "Choose a file...")
            self.assertEqual(len(form.fields['data_file'].choices), n_files)
        elif response_method == "POST" and selected_file == "Choose a file...":
            self.assertFalse(form.is_valid())
            self.assertTrue(form.is_bound)
            self.assertEqual(form.fields['data_file'].initial, "Choose a file...")
            self.assertEqual(len(form.fields['data_file'].choices), n_files)
        else:
            # self.assertTrue(form.is_valid())
            self.assertTrue(form.is_bound)
            self.assertEqual(form.fields['data_file'].initial, selected_file)

    def _verify_file_selection_enabled(self, context, is_enabled):
        form = context['datafile_form']
        self.assertEquals(context['error_message'], None)
        if is_enabled:
            self.assertFalse(context['select_btn_disabled'])
            self.assertTrue(context['change_btn_disabled'])
            self.assertFalse(context['container_visible'])
            self.assertFalse(form.fields['data_file'].disabled)
        else:
            self.assertTrue(context['select_btn_disabled'])
            self.assertFalse(context['change_btn_disabled'])
            self.assertTrue(context['container_visible'])
            self.assertTrue(form.fields['data_file'].disabled)

    def _verify_container_content(self, context, filename, dataframe):
        self.assertEqual(context['data_file_name'], filename)
        self.assertEqual(context['data_file_rows'], dataframe.shape[0])
        self.assertEqual(context['data_file_cols'], dataframe.shape[1])
        self.assertEqual(context['target_feature'], dataframe.columns[-1])
        self.assertEqual(context['base_features'], dataframe.shape[1] - 1)
        self.assertEqual(context['training_rows'], int(dataframe.shape[0] * 0.8))
        self.assertEqual(context['validation_rows'], dataframe.shape[0] - int(dataframe.shape[0] * 0.8))

    def _verify_validation_content(self, context, is_enabled):
        if not is_enabled:
            self.assertTrue(context['validation_disabled'])
            self.assertEqual(context['active_tab'], "explore")
        else:
            self.assertFalse(context['validation_disabled'])
            self.assertEqual(context['active_tab'], "validate")
            self.assertEqual(context['training_method'], "Linear Regression")
            self.assertGreater(float(context['validation_score']), 0)
            self.assertGreater(float(context['training_score']), 0)
