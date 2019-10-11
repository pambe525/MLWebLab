import os
import os.path
from pandas import read_csv
from mlflow.forms import DataFileForm, ControlPanelForm
from django.conf import settings
from pandas import read_json
from mlflow.methods import fit_linear_regression


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
def set_control_panel_context(context, form, file_name, data_frame):
    context['control_form'] = form
    training_ratio = form.fields['training_ratio'].initial
    context['data_file_name'] = file_name
    context['data_file_rows'] = int(data_frame.shape[0])
    context['data_file_cols'] = int(data_frame.shape[1])
    context['target_feature'] = data_frame.columns[-1]
    context['base_features'] = data_frame.shape[1] - 1
    context['training_rows'] = int(data_frame.shape[0] * training_ratio)
    context['validation_rows'] = context['data_file_rows'] - context['training_rows']
    context['validation_disabled'] = True
    context['active_tab'] = "explore"
    context['training_method'] = form.fields['training_method'].initial
    return context


# Sets validation content
def set_validation_context(context, fit_result):
    context["validation_score"] = round(fit_result['validation_score'], 2)
    context["training_score"] = round(fit_result['training_score'], 2)
    context["validation_disabled"] = False
    context["active_tab"] = "validate"


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
    context = {"error_message": None}
    datafile_form = DataFileForm() if request.method != "POST" else DataFileForm(request.POST)
    control_form = ControlPanelForm() if request.method != "POST" else ControlPanelForm(request.POST)
    set_file_selection_context(context, datafile_form, True)
    if datafile_form.is_valid():
        file_name = datafile_form.cleaned_data['data_file']
        datafile_form.fields['data_file'].initial = file_name
        try:
            data_frame = read_csv_datafile(file_name)
            set_file_selection_context(context, datafile_form, False)
            set_control_panel_context(context, control_form, file_name, data_frame)
            request.session['datafile'] = file_name
            request.session['dataframe'] = data_frame.to_json()
        except Exception as e:
            context['error_message'] = str(e)
    elif "train_btn" in request.POST:
        file_name = request.session['datafile']
        data_frame = read_json(request.session['dataframe'])
        datafile_form.fields['data_file'].initial = file_name
        set_file_selection_context(context, datafile_form, False)
        set_control_panel_context(context, control_form, file_name, data_frame)
        try:
            fit_result = fit_linear_regression(data_frame, control_form.fields['training_ratio'].initial)
            set_validation_context(context, fit_result)
        except Exception as e:
            context["error_message"] = str(e)
    return context
