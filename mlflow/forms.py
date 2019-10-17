import os
from os import listdir as current_dir
from os.path import isfile

from django import forms

from mlflow import constants


# Static function to read data files from data directory
def get_datafile_choices():
    dir_items = current_dir(constants.DATA_FILE_PATH)
    choices = [constants.FILE_SELECT_DEFAULT]
    for f in dir_items:
        if isfile(os.path.join(constants.DATA_FILE_PATH, f)):
            choices.append(f)
    return [(filename, filename.rsplit('.', 1)[0]) for filename in choices]


# DataFileForm for File Selection
class DataFileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DataFileForm, self).__init__(*args, **kwargs)
        file_choices = get_datafile_choices()
        self.fields['data_file'] = forms.ChoiceField(label="Data File", choices=file_choices)
        self.fields['data_file'].initial = file_choices[0][0]
        self.fields['data_file'].widget.attrs['class'] = constants.FILE_SELECT_WIDGET_CLASS

    def is_valid(self):
        valid = super(DataFileForm, self).is_valid()
        if valid and self.cleaned_data.get('data_file') == self.fields['data_file'].choices[0][0]:
            valid = False
        return valid


# ControlPanelForm in sidebar
class ControlPanelForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ControlPanelForm, self).__init__(*args, **kwargs)
        # self.fields['data_file_name'] = forms.CharField(widget=forms.HiddenInput)
        self.fields['training_method'] = forms.ChoiceField(choices=constants.TRAINING_METHOD_CHOICES)
        self.fields['training_ratio'] = forms.ChoiceField(choices=constants.TRAINING_RATIO_CHOICES)
        self.fields['training_method'].widget.attrs['class'] = constants.CONTROL_PANEL_WIDGET_CLASS
        self.fields['training_ratio'].widget.attrs['class'] = constants.CONTROL_PANEL_WIDGET_CLASS
        self.fields['training_method'].initial = constants.TRAINING_METHOD_INITIAL
        self.fields['training_ratio'].initial = constants.TRAINING_RATIO_INITIAL
