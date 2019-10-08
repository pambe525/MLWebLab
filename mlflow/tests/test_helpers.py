import os
from django.test import SimpleTestCase
from unittest.mock import MagicMock, patch
from mlflow.helpers import set_file_selection_context
from mlflow.helpers import dataframe_has_headers
from mlflow.helpers import set_default_container_context
from mlflow.helpers import get_context
from mlflow.helpers import read_csv_datafile
from django.conf import settings
from pandas import DataFrame
from pandas.errors import EmptyDataError


class HelperStaticFunctionsTestCase(SimpleTestCase):

    def test_set_file_selection_context_with_enabled(self):
        context = {}
        form = MagicMock()
        context = set_file_selection_context(context, form, True)
        self.assertEqual(context["file_selection_form"], form)
        self.assertFalse(context["select_btn_disabled"])
        self.assertTrue(context["change_btn_disabled"])
        self.assertFalse(context["container_visible"])
        self.assertIsNone(context["error_message"])

    def test_set_file_selection_context_with_disabled(self):
        context = {}
        form = MagicMock()
        context = set_file_selection_context(context, form, False)
        self.assertEqual(context["file_selection_form"], form)
        self.assertTrue(context["select_btn_disabled"])
        self.assertFalse(context["change_btn_disabled"])
        self.assertTrue(context["container_visible"])
        self.assertIsNone(context["error_message"])

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
        context = set_default_container_context(context, filename, data_frame)
        self.assertEqual(context['data_file_name'], filename)
        self.assertEqual(context['data_file_rows'], 4)
        self.assertEqual(context['data_file_cols'], 5)
        self.assertEqual(context['target_feature'], "Col5")
        self.assertEqual(context['base_features'], 4)
        self.assertEqual(context['training_ratio'], "80%")
        self.assertEqual(context['training_rows'], 3)
        self.assertEqual(context['training_method'], "Linear Regression")
        self.assertEqual(context['validation_rows'], 1)
        self.assertEqual(context['validation_score'], "")
        self.assertTrue(context['validation_disabled'])
        self.assertEqual(context['active_tab'], "explore")

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
        with patch("mlflow.helpers.get_datafile_choices") as mock_datafile_list:
            file_choices = [("Choose a file...", "Choose a file..."), ("a1.txt", "a1.txt"), ("a2.txt", "a2.txt")]
            mock_datafile_list.return_value = file_choices
            mock_response = MagicMock()
            mock_response.method = "GET"
            context = get_context(mock_response)
            mock_datafile_list.assert_called_once()
            self.__verify_file_selection_form(context, "GET", len(file_choices))
            self.__verify_file_selection_enabled(context, True)

    def test_get_context_with_POST_response_and_no_file_selected(self):
        with patch("mlflow.helpers.get_datafile_choices") as mock_datafile_list:
            file_choices = [("Choose a file...", "Choose a file..."), ("a1.txt", "a1.txt"), ("a2.txt", "a2.txt")]
            mock_datafile_list.return_value = file_choices
            mock_response = MagicMock()
            mock_response.method = "POST"
            mock_response.POST = {"data_file": "Choose a file..."}
            context = get_context(mock_response)
            self.__verify_file_selection_form(context, "POST", len(file_choices))

    def test_get_context_with_POST_and_file_selected(self):
        data = {"Col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "Col3": [9, 10, 11, 12],
                "Col4": [13, 14, 15, 16], "Col5": [17, 18, 19, 20]}
        with patch("mlflow.helpers.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices = [("Choose a file...", "Choose a file..."), ("a1.txt", "a1.txt"), ("a2.txt", "a2.txt")]
                mock_datafile_list.return_value = file_choices
                mock_csv_read.return_value = DataFrame(data)
                mock_response = MagicMock()
                mock_response.method = "POST"
                mock_response.POST = {"data_file": "a2.txt", "select_btn": []}
                context = get_context(mock_response)
                mock_csv_read.assert_called_once()
                self.__verify_file_selection_form(context, "POST", len(file_choices), selected_file="a2.txt")
                self.__verify_file_selection_enabled(context, False)
                self.__verify_container_content(context, "a2.txt", mock_csv_read.return_value)

    def test_get_context_with_POST_and_read_exception(self):
        with patch("mlflow.helpers.get_datafile_choices") as mock_datafile_list:
            with patch("mlflow.helpers.read_csv_datafile") as mock_csv_read:
                file_choices = [("Choose a file...", "Choose a file..."), ("a1.txt", "a1.txt"), ("a2.txt", "a2.txt")]
                mock_datafile_list.return_value = file_choices
                mock_csv_read.side_effect = Exception("Error occurred")
                mock_response = MagicMock()
                mock_response.method = "POST"
                mock_response.POST = {"data_file": "a2.txt", "select_btn": []}
                try:
                    context = get_context(mock_response)
                except Exception as e:
                    self.__verify_file_selection_form(context, "POST", len(file_choices), selected_file="a2.txt")
                    self.__verify_file_selection_enabled(context, True)

    # ------------------------------------------------------------------------------------------------------------------
    def __verify_file_selection_form(self, context, response_method, n_files, selected_file="Choose a file..."):
        form = context['datafile_form']
        if response_method == "GET" or (response_method == "POST" and selected_file == "Choose a file..."):
            self.assertFalse(form.is_valid())
            self.assertFalse(form.is_bound)
            self.assertEqual(form.fields['data_file'].initial, "Choose a file...")
            self.assertEqual(len(form.fields['data_file'].choices), n_files)
            self.assertEqual(form.fields['data_file'].choices[0], ("Choose a file...", "Choose a file..."))
        else:
            self.assertTrue(form.is_valid())
            self.assertTrue(form.is_bound)
            self.assertEqual(form.fields['data_file'].initial, selected_file)

    def __verify_file_selection_enabled(self, context, is_enabled):
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

    def __verify_container_content(self, context, filename, dataframe):
        self.assertEqual(context['data_file_name'], filename)
        self.assertEqual(context['data_file_rows'], dataframe.shape[0])
        self.assertEqual(context['data_file_cols'], dataframe.shape[1])
        self.assertEqual(context['target_feature'], dataframe.columns[-1])
        self.assertEqual(context['base_features'], dataframe.shape[0]-1)
        self.assertEqual(context['training_ratio'], "80%")
        self.assertEqual(context['training_rows'], int(dataframe.shape[0]*0.8))
        self.assertEqual(context['training_method'], "Linear Regression")
        self.assertEqual(context['validation_rows'], dataframe.shape[0]-int(dataframe.shape[0]*0.8))
        self.assertEqual(context['validation_score'], "")
        self.assertTrue(context['validation_disabled'])
        self.assertEqual(context['active_tab'], "explore")
