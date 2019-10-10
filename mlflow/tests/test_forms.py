from django.test import SimpleTestCase
from django.conf import settings
from mlflow.forms import DataFileForm, get_datafile_choices
from mlflow.forms import ControlPanelForm
from unittest.mock import patch
import os.path


class DataFileForm_TestCase(SimpleTestCase):

    @patch('mlflow.forms.current_dir')
    @patch('mlflow.forms.isfile')
    def test_get_datafile_choices_returns_datafile_names(self, mock_isfile, mock_current_dir):
        datafiles_path = os.path.join(settings.BASE_DIR, 'data')
        datafile_choices = ["file1.dat", "file2.txt", "directory", "file3.dat"]
        mock_isfile.side_effect = [True, True, False, True]
        mock_current_dir.return_value = datafile_choices
        file_names = get_datafile_choices()
        mock_current_dir.assert_called_once_with(datafiles_path)
        self.assertEqual(len(file_names), 4)
        self.assertEqual(file_names[0], ("Choose a file...", "Choose a file..."))
        self.assertEqual(file_names[3], ("file3.dat", "file3.dat"))

    def test_Unbound_DataFileForm(self):
        self.__verify_form(None, False)

    def test_Bound_But_Invalid_DataFileForm(self):
        self.__verify_form({'data_file': 'Choose a file...'}, False)

    def test_Bound_And_Valid_DataFileForm(self):
        self.__verify_form({'data_file': 'file2.dat'}, True)

    def __verify_form(self, bound_data, is_valid):
        with patch("mlflow.forms.isfile") as mock_isfile:
            with patch("mlflow.forms.current_dir") as mock_listdir:
                mock_listdir.return_value = ['file1.dat', 'file2.dat', 'file3.dat']
                mock_isfile.side_effects = [True, True, True]
                form = DataFileForm() if bound_data is None else DataFileForm(bound_data)
        datafiles_path = os.path.join(settings.BASE_DIR, 'data')
        mock_listdir.assert_called_once_with(datafiles_path)
        self.assertTrue(form.is_valid()) if is_valid else self.assertFalse(form.is_valid())
        self.assertEquals(form.fields['data_file'].initial, "Choose a file...")
        self.assertEqual(len(form.fields['data_file'].choices), 4)
        self.assertTrue(('file2.dat', 'file2.dat') in form.fields['data_file'].choices)


class ControlPanelForm_TestCase(SimpleTestCase):

    def test_instantiation(self):
        form = ControlPanelForm()
        self.assertFalse(form.is_valid())
        self.assertFalse(form.is_bound)
        self.assertEqual(len(form.fields['training_method'].choices), 1)
        self.assertEqual(form.fields['training_method'].choices[0][1], "Linear Regression")
        self.assertEqual(len(form.fields['training_ratio'].choices), 1)
        self.assertEqual(form.fields['training_ratio'].choices[0][1], "80%")
        self.assertEqual(form.fields['training_method'].initial, "linear_reg")
        self.assertEqual(form.fields['training_ratio'].initial, 0.8)


    def test_instantiation_with_POST_data(self):
        post_data = {"training_ratio": 0.8, "training_method": "linear_reg"}
        form = ControlPanelForm(post_data)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('training_ratio'), "0.8")
        self.assertEqual(form.cleaned_data.get('training_method'), "linear_reg")


