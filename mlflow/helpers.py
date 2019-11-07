import os
import os.path
import json

from pandas import read_csv

from mlflow import constants
from mlflow.forms import DataFileForm, ControlPanelForm


# Sets context dict parameters when file selection is enabled or disabled
def set_file_selection_context(context, form, is_enabled):
    context['datafile_form'] = form
    context['container_visible'] = False if is_enabled else True
    context['error_message'] = None
    return context


# Sets default context dict parameters for home page content container
def set_control_panel_context(context, form, file_name, data_frame):
    context['control_form'] = form
    training_ratio = form.fields['n_splits'].initial
    context['data_file_name'] = file_name
    context['data_file_rows'] = int(data_frame.shape[0])
    context['data_file_cols'] = int(data_frame.shape[1])
    context['target_feature'] = data_frame.columns[-1]
    context['active_tab'] = "data_summary"
    context['training_method'] = form.fields['training_method'].initial
    return context


# Compute features summary
def set_features_summary(context, data_frame):
    summary = []
    for feature_name in data_frame.columns:
        feature_stats = {
            'name': feature_name, 'type': str(data_frame.dtypes[feature_name]),
            'min': round(data_frame[feature_name].min(), 2),
            'max': round(data_frame[feature_name].max(), 2),
            'mean': round(data_frame[feature_name].mean(), 2),
            'stdev': round(data_frame[feature_name].std(), 2)
        }
        summary.append(feature_stats)
    context['features_summary'] = summary


# Set data_frame
def set_data_frame(context, data_frame):
    context['data_frame'] = data_frame.to_json()


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
    file_path = os.path.join(constants.DATA_FILE_PATH, file_name)
    dataFrame = read_csv(file_path)
    if int(dataFrame.shape[1]) < 2:
        raise Exception("Data file has only one column. Add at least one more column.")
    if not dataframe_has_headers(dataFrame):
        raise Exception("Data file has no headers. Add non-numeric column headers.")
    if int(dataFrame.shape[0]) < 10:
        raise Exception("Data file has fewer than 10 records (must have at least 10 records)")
    return dataFrame


# Returns forms based on request
def initialize_forms(request):
    datafile_form = DataFileForm() if request.method != "POST" else DataFileForm(request.POST)
    control_form = ControlPanelForm() if request.method != "POST" else ControlPanelForm(request.POST)
    return control_form, datafile_form


# HomeView Context Manager to manage all page variables and state
def get_context(request):
    context = {"error_message": None}
    control_form, datafile_form = initialize_forms(request)
    set_file_selection_context(context, datafile_form, True)
    if datafile_form.is_valid():
        file_name = datafile_form.cleaned_data['data_file']
        datafile_form.fields['data_file'].initial = file_name
        try:
            data_frame = read_csv_datafile(file_name)
            set_file_selection_context(context, datafile_form, False)
            set_control_panel_context(context, control_form, file_name, data_frame)
            set_features_summary(context, data_frame)
            set_data_frame(context, data_frame)
            request.session['datafile'] = file_name
            request.session['dataframe'] = data_frame.to_json()
        except Exception as e:
            context['error_message'] = str(e)
    return context
