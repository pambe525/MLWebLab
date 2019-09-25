from django import forms
from django.conf import settings
from os import listdir as current_dir
import os.path


def get_datafile_choices():
    datafiles_path = os.path.join(settings.BASE_DIR, 'data')
    dir_items = current_dir(datafiles_path)
    choices = ["Choose a file..."]
    for f in dir_items:
        if os.path.isfile(os.path.join(datafiles_path, f)):
            choices.append(f)
    return [(filename, filename) for filename in choices]


class DataFileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DataFileForm, self).__init__(*args, **kwargs)
        self.fields['data_file'] = forms.ChoiceField(label="Data File", choices=get_datafile_choices())
        self.fields['data_file'].initial = "Choose a file..."
