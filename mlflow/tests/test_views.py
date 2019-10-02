from django.test import SimpleTestCase
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch
import os.path
from pandas import DataFrame
from pandas.errors import EmptyDataError


class HomeViewTestCase(SimpleTestCase):
    datafile_choices = ["file1.dat", "file2.txt", "file3.dat"]

    @patch("mlflow.forms.os.path.isfile")
    @patch("mlflow.forms.current_dir")
    def test_home_view_loads_file_selection_list(self, mock_listdir, mock_isfile):
        mock_listdir.return_value = self.datafile_choices
        mock_isfile.side_effect = [True, True, True]
        response = self.client.get(reverse("index"))
        # Verify form contains Select field with correct choices
        self.__validate_form_state(response, False, False, "Choose a file...")
        self.__validate_file_selection_enabled(response, True)
        self.assertEquals(response.context['error_message'], None)

    def test_home_view_with_default_selection(self):
        post_data = {'data_file': 'Choose a file...'}
        response = self.__make_datafile_selected_request(post_data)
        # Verify form contains Select field with correct choices
        self.__validate_form_state(response, False, True, "Choose a file...")
        self.__validate_file_selection_enabled(response, True)
        self.assertEquals(response.context['error_message'], None)

    def test_home_view_with_a_file_selected(self):
        data = {"col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "col3": [9, 10, 11, 12],
                "col4": [13, 14, 15, 16], "col5": [17, 18, 19, 20]}
        response = self.__make_datafile_selected_request_with_mock_read_csv(data)
        self.__validate_form_state(response, True, True, "file2.txt")
        self.__validate_file_selection_enabled(response, False)
        self.__validate_source_file_data(response, 'file2.txt', 4, 5)
        self.__validate_training_set_data(response, 'col5', 4, '80%', 3)
        self.__validate_method_data(response, "Linear Regression")
        self.__validate_validation_set_data(response, 1, "")
        self.assertEquals(response.context['error_message'], None)

    def test_home_view_with_read_exception(self):
        with patch("mlflow.views.read_csv") as mock_read_csv:
            mock_read_csv.side_effect = EmptyDataError("No data in file")
            response = self.__make_datafile_selected_request({'data_file': 'file2.txt'})
            mock_read_csv.assert_called_once()
        self.__validate_form_state(response, True, True, "file2.txt")
        self.__validate_file_selection_enabled(response, True)
        self.assertEquals(response.context['error_message'], "No data in file")

    def test_home_view_with_error_on_data_with_one_column(self):
        data = {"col1": [1, 2, 3, 4]}
        response = self.__make_datafile_selected_request_with_mock_read_csv(data)
        self.__validate_form_state(response, True, True, "file2.txt")
        self.__validate_file_selection_enabled(response, True)
        self.assertEquals(response.context['error_message'], "Data file has only one column")

    def test_home_view_with_error_on_data_with_numeric_headers(self):
        data = {"1.5": [1.1, 2.1, 3.1], "2.2": [1.2, 2.2, 3.2], "col3": [1.3, 2.3, 3.3]}
        response = self.__make_datafile_selected_request_with_mock_read_csv(data)
        self.__validate_form_state(response, True, True, "file2.txt")
        self.__validate_file_selection_enabled(response, True)
        self.assertEquals(response.context['error_message'], "Data file has no headers")

    # ------------------------------------------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------------------------------------------

    def __make_datafile_selected_request(self, post_data):
        post_data['select_btn'] = []
        with patch("mlflow.forms.os.path.isfile") as mock_isfile:
            with patch("mlflow.forms.current_dir") as mock_listdir:
                # Setup mock listdir and isfile used in views.py to return fake values
                mock_listdir.return_value = self.datafile_choices
                mock_isfile.side_effect = [True, True, True]
                response = self.client.post(reverse("index"), post_data)
        # Verify listdir is called with correct path
        datafiles_path = os.path.join(settings.BASE_DIR, 'data')
        mock_listdir.assert_called_once_with(datafiles_path)
        return response

    def __make_datafile_selected_request_with_mock_read_csv(self, data):
        with patch("mlflow.views.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            response = self.__make_datafile_selected_request({'data_file': 'file2.txt'})
            datafiles_path = os.path.join(settings.BASE_DIR, 'data/file2.txt')
            mock_read_csv.assert_called_once_with(datafiles_path)
        return response

    def __validate_form_state(self, response, is_valid, is_bound, initial):
        form = response.context['form']
        self.assertTrue(form.is_valid()) if is_valid else self.assertFalse(form.is_valid())
        self.assertTrue(form.is_bound) if is_bound else self.assertFalse(form.is_bound)
        self.assertEqual(form.fields['data_file'].initial, initial)
        self.assertEqual(len(form.fields['data_file'].choices), len(self.datafile_choices) + 1)
        self.assertEqual(form.fields['data_file'].choices[0], ("Choose a file...", "Choose a file..."))
        self.assertEqual(form.fields['data_file'].choices[2], (self.datafile_choices[1], self.datafile_choices[1]))

    def __validate_file_selection_enabled(self, response, is_enabled):
        form = response.context['form']
        if is_enabled:
            self.assertEquals(response.context['select_btn_disabled'], '')
            self.assertEquals(response.context['change_btn_disabled'], 'disabled')
            self.assertEquals(response.context['flow_chart_visibility'], 'invisible')
            self.assertFalse(form.fields['data_file'].disabled)
        else:
            self.assertEquals(response.context['select_btn_disabled'], 'disabled')
            self.assertEquals(response.context['change_btn_disabled'], '')
            self.assertEquals(response.context['flow_chart_visibility'], 'visible')
            self.assertTrue(form.fields['data_file'].disabled)

    def __validate_source_file_data(self, response, file_name, rows, cols):
        self.assertEquals(file_name, response.context['data_file_name'])
        self.assertEquals(rows, response.context['data_file_rows'])
        self.assertEquals(cols, response.context['data_file_cols'])

    def __validate_training_set_data(self, response, target_feature, base_features, training_ratio, training_rows):
        self.assertEquals(target_feature, response.context["target_feature"])
        self.assertEquals(base_features, response.context["base_features"])
        self.assertEquals(training_ratio, response.context["training_ratio"])
        self.assertEquals(training_rows, response.context["training_rows"])

    def __validate_method_data(self, response, training_method):
        self.assertEquals(training_method, response.context["training_method"])

    def __validate_validation_set_data(self, response, validation_rows, validation_score):
        self.assertEquals(validation_rows, response.context["validation_rows"])
        self.assertEquals(validation_score, response.context["validation_score"])
