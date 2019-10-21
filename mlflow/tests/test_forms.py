from unittest.mock import patch

from django.test import SimpleTestCase

from mlflow import constants
from mlflow.forms import ControlPanelForm
from mlflow.forms import DataFileForm, get_datafile_choices


class DataFileForm_TestCase(SimpleTestCase):

    @patch('mlflow.forms.current_dir')
    @patch('mlflow.forms.isfile')
    def test_get_datafile_choices_returns_datafile_names(self, mock_isfile, mock_current_dir):
        datafiles_path = constants.DATA_FILE_PATH
        datafile_choices = ["file1.dat", "file2.txt", "directory", "file3.dat"]
        mock_isfile.side_effect = [True, True, False, True]
        mock_current_dir.return_value = datafile_choices
        file_names = get_datafile_choices()
        mock_current_dir.assert_called_once_with(datafiles_path)
        self.assertEqual(len(file_names), 4)
        self.assertEqual(file_names[0], (constants.FILE_SELECT_DEFAULT, constants.FILE_SELECT_DEFAULT))
        self.assertEqual(file_names[3], ("file3.dat", "file3"))

    def test_Unbound_DataFileForm(self):
        self._verify_form(is_valid=False)

    def test_Bound_But_Invalid_DataFileForm(self):
        self._verify_form({'data_file': 'Choose'}, is_valid=False)

    def test_Bound_And_Valid_DataFileForm(self):
        self._verify_form(bound_data={'data_file': 'file2.dat'}, is_valid=True)

    def _verify_form(self, bound_data=None, is_valid=False):
        with patch("mlflow.forms.get_datafile_choices") as mock_datafile_choices:
            choices = [("Choose", "Choose"), ("file1.dat", "file1"), ("file2.dat", "file2"), ("file3.dat", "file3")]
            mock_datafile_choices.return_value = choices
            form = DataFileForm() if bound_data is None else DataFileForm(bound_data)
        mock_datafile_choices.assert_called_once()
        self.assertTrue(form.is_valid()) if is_valid else self.assertFalse(form.is_valid())
        self.assertEquals(form.fields['data_file'].initial, choices[0][0])
        self.assertEqual(len(form.fields['data_file'].choices), 4)
        self.assertTrue(('file2.dat', 'file2') in form.fields['data_file'].choices)


class ControlPanelForm_TestCase(SimpleTestCase):

    def test_instantiation(self):
        form = ControlPanelForm()
        self.assertFalse(form.is_valid())
        self.assertFalse(form.is_bound)
        self.assertEqual(len(form.fields['training_method'].choices), 1)
        self.assertEqual(form.fields['training_method'].choices[0][1], constants.TRAINING_METHOD_CHOICES[0][1])
        self.assertEqual(len(form.fields['training_ratio'].choices), 1)
        self.assertEqual(form.fields['training_ratio'].choices[0][1], constants.TRAINING_RATIO_CHOICES[0][1])
        self.assertEqual(form.fields['training_method'].initial, constants.TRAINING_METHOD_INITIAL)
        self.assertEqual(form.fields['training_ratio'].initial, constants.TRAINING_RATIO_INITIAL)

    def test_instantiation_with_POST_data(self):
        post_data = {"training_ratio": constants.TRAINING_RATIO_INITIAL,
                     "training_method": constants.TRAINING_METHOD_INITIAL}
        form = ControlPanelForm(post_data)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('training_ratio'), str(constants.TRAINING_RATIO_INITIAL))
        self.assertEqual(form.cleaned_data.get('training_method'), constants.TRAINING_METHOD_INITIAL)
