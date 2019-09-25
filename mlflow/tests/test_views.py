from django.test import SimpleTestCase
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch
import os.path


class HomeViewTestCase(SimpleTestCase):

    @patch("mlflow.forms.os.path.isfile")
    @patch("mlflow.forms.current_dir")
    def test_home_view_get_creates_datafiles_list(self, mock_listdir, mock_isfile):
        # Setup mock listdir and isfile used in views.py to return fake values
        mock_listdir.return_value = ["file1.dat", "file2.txt", "file3.dat"]
        mock_isfile.side_effect = [True, True, True]
        # Invoke home_view using GET
        response = self.client.get(reverse("index"))
        # Verify listdir is called with correct path
        datafiles_path = os.path.join(settings.BASE_DIR, 'data')
        mock_listdir.assert_called_once_with(datafiles_path)
        # Verify form contains Select field with correct choices
        form = response.context['form']
        self.assertEqual(len(form.fields['data_file'].choices), 4)
        self.assertEqual(form.fields['data_file'].choices[0], ("Choose a file...", "Choose a file..."))
        self.assertEqual(form.fields['data_file'].choices[2], ("file2.txt", "file2.txt"))
        self.assert_no_file_selected_context(response)

    @patch("mlflow.forms.os.path.isfile")
    @patch("mlflow.forms.current_dir")
    def test_home_view_post_with_default_selection(self, mock_listdir, mock_isfile):
        # Setup mock listdir and isfile used in views.py to return fake values
        mock_listdir.return_value = ["file1.dat", "file2.txt", "file3.dat"]
        mock_isfile.side_effect = [True, True, True]
        # Invoke home_view using POST
        response = self.client.post(reverse("index"), {'data_file': ['Choose a file...'], 'select_btn': ['']})
        # Verify listdir is called with correct path
        datafiles_path = os.path.join(settings.BASE_DIR, 'data')
        mock_listdir.assert_called_once_with(datafiles_path)
        # Verify form contains Select field with correct choices
        form = response.context['form']
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assert_no_file_selected_context(response)

    @patch("mlflow.forms.os.path.isfile")
    @patch("mlflow.forms.current_dir")
    def test_home_view_post_with_file_selected(self, mock_listdir, mock_isfile):
        # Setup mock listdir and isfile used in views.py to return fake values
        mock_listdir.return_value = ["file1.dat", "file2.txt", "file3.dat"]
        mock_isfile.side_effect = [True, True, True]
        # Invoke home_view using POST
        response = self.client.post(reverse("index"), {'data_file': ['file2.txt']})
        form = response.context['form']
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_bound)
        self.assert_file_selected_context(response, 'file2.txt')
        self.assert_source_file_data(response, 'file2.txt', 97, 2)

    # ------------------------------------------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------------------------------------------

    def assert_no_file_selected_context(self, response):
        form = response.context['form']
        self.assertEquals(response.context['select_btn_disabled'], '')
        self.assertEquals(response.context['change_btn_disabled'], 'disabled')
        self.assertEquals(response.context['flow_chart_visibility'], 'invisible')
        self.assertEquals(response.context['error_message'], None)
        self.assertFalse(form.fields['data_file'].disabled)
        self.assertEquals(form.fields['data_file'].initial, "Choose a file...")

    def assert_file_selected_context(self, response, filename):
        form = response.context['form']
        self.assertEquals(response.context['select_btn_disabled'], 'disabled')
        self.assertEquals(response.context['change_btn_disabled'], '')
        self.assertEquals(response.context['flow_chart_visibility'], 'visible')
        self.assertTrue(form.fields['data_file'].disabled)
        self.assertEquals(response.context['error_message'], None)
        self.assertEquals(form.fields['data_file'].initial, filename)

    def assert_source_file_data(self, response, file_name, rows, cols):
        self.assertEquals(file_name, response.context['data_file_name'])
        self.assertEquals(rows, response.context['data_file_rows'])
        self.assertEquals(cols, response.context['data_file_cols'])
