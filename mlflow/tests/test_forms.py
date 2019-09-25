from django.test import SimpleTestCase
from django.conf import settings
from mlflow.forms import DataFileForm
from unittest.mock import patch
import os.path


class FormsTestCase(SimpleTestCase):

    @patch("mlflow.forms.os.path.isfile")
    @patch("mlflow.forms.current_dir")
    def test_DataFileForm_ChoiceField(self, mock_listdir, mock_isfile):
        mock_listdir.return_value = ['file1.dat', 'file2.dat', 'file3.dat']
        mock_isfile.side_effects = [True, True, True]
        form = DataFileForm()
        datafiles_path = os.path.join(settings.BASE_DIR, 'data')
        mock_listdir.assert_called_once_with(datafiles_path)
        mock_listdir.assert_called_once()
        self.assertFalse(form.is_valid())
        self.assertEquals(form.fields['data_file'].initial, "Choose a file...")
        self.assertEqual(len(form.fields['data_file'].choices), 4)
        self.assertTrue(('file2.dat', 'file2.dat') in form.fields['data_file'].choices)
