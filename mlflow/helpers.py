import os
import os.path
from pandas import read_csv
from mlflow.forms import DataFileForm, ControlPanelForm
from django.conf import settings


# Sets context dict parameters when file selection is enabled or disabled
def set_file_selection_context(context, form, is_enabled):
    context['datafile_form'] = form
    context['select_btn_disabled'] = False if is_enabled else True
    context['change_btn_disabled'] = True if is_enabled else False
    context['container_visible'] = False if is_enabled else True
    context['error_message'] = None
    form.fields["data_file"].disabled = False if is_enabled else True
    return context


# Sets default context dict parameters for home page content container
def set_default_container_context(context, file_name, data_frame):
    training_ratio = 0.8
    context['data_file_name'] = file_name
    context['data_file_rows'] = int(data_frame.shape[0])
    context['data_file_cols'] = int(data_frame.shape[1])
    context['target_feature'] = data_frame.columns[-1]
    context['base_features'] = data_frame.shape[1] - 1
    context['training_ratio'] = str(int(training_ratio * 100)) + "%"
    context['training_rows'] = int(data_frame.shape[0] * training_ratio)
    context['training_method'] = "Linear Regression"
    context['validation_rows'] = context['data_file_rows'] - context['training_rows']
    context['validation_score'] = ""
    context['validation_disabled'] = True
    context['active_tab'] = "explore"
    return context


# Finds if a pandas data frame has headers
def dataframe_has_headers(data_frame):
    for header in data_frame.columns:
        try:
            float(header)
            return False
        except ValueError:
            continue
    return True


# Reads csv data file and returns a pandas DataFrame object (also checks for date file errors)
def read_csv_datafile(file_name):
    file_path = os.path.join(settings.BASE_DIR, 'data/' + file_name)
    dataFrame = read_csv(file_path)
    if int(dataFrame.shape[1]) < 2: raise Exception("Data file has only one column")
    if int(dataFrame.shape[0]) < 2: raise Exception("Data file has only one row")
    if not dataframe_has_headers(dataFrame):
        raise Exception("Data file has no headers")
    return dataFrame


# HomeView Context Manager to manage all page variables and state
def get_context(request):
    context = {"answer": request.POST}
    datafile_form = DataFileForm() if request.method != "POST" else DataFileForm(request.POST)
    set_file_selection_context(context, datafile_form, True)
    if datafile_form.is_valid():
        file_name = datafile_form.cleaned_data['data_file']
        datafile_form.fields['data_file'].initial = file_name
        try:
            data_frame = read_csv_datafile(file_name)
            set_file_selection_context(context, datafile_form, False)
            set_default_container_context(context, file_name, data_frame)
        except Exception as e:
            context['error_message'] = str(e)
    return context
