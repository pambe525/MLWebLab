from django import forms
import os
from os import listdir as current_dir
from os.path import isfile
from django.conf import settings


# Static function to read data files from data directory
def get_datafile_choices():
    datafiles_path = os.path.join(settings.BASE_DIR, 'data')
    dir_items = current_dir(datafiles_path)
    choices = ["Choose a file..."]
    for f in dir_items:
        if isfile(os.path.join(datafiles_path, f)):
            choices.append(f)
    return [(filename, filename) for filename in choices]


# DataFileForm for File Selection
class DataFileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DataFileForm, self).__init__(*args, **kwargs)
        file_choices = get_datafile_choices()
        self.fields['data_file'] = forms.ChoiceField(label="Data File", choices=file_choices)
        self.fields['data_file'].initial = "Choose a file..."
        self.fields['data_file'].widget.attrs['class'] = 'input-group-text custom-select'

    def is_valid(self):
        valid = super(DataFileForm, self).is_valid()
        if valid and self.cleaned_data.get('data_file') == "Choose a file...":
            valid = False
        return valid
