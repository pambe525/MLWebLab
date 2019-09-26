from django.test import SimpleTestCase
from django.conf import settings
from mlflow.forms import DataFileForm
from unittest.mock import patch
import os.path


class DataFileForm_TestCase(SimpleTestCase):

    def test_Unbound_DataFileForm(self):
        self.__verify_form(None, False)

    def test_Bound_But_Invalid_DataFileForm(self):
        self.__verify_form({'data_file': 'Choose a file...'}, False)

    def test_Bound_And_Valid_DataFileForm(self):
        self.__verify_form({'data_file': 'file2.dat'}, True)

    def __verify_form(self, bound_data, is_valid):
        with patch("mlflow.forms.os.path.isfile") as mock_isfile:
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
