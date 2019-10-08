from django import forms
from mlflow.helpers import get_datafile_choices


# DataFileForm for File Selection
class DataFileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DataFileForm, self).__init__(*args, **kwargs)
        self.fields['data_file'] = forms.ChoiceField(label="Data File", choices=get_datafile_choices())
        self.fields['data_file'].initial = "Choose a file..."
        self.fields['data_file'].widget.attrs['class'] = 'input-group-text custom-select'

    def is_valid(self):
        valid = super(DataFileForm, self).is_valid()
        if valid and self.cleaned_data.get('data_file') == "Choose a file...":
            valid = False
        return valid
