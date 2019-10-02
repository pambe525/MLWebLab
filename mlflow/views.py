import os
import os.path
from django.shortcuts import render
from pandas import read_csv
from mlflow.forms import DataFileForm
from django.conf import settings


def home_view(request):
    context = {'error_message': None}
    __set_context_for_file_selection_enabled(True, context)
    form = DataFileForm()
    context['form'] = form
    return render(request, 'home.html', context)


def datafile_selected(request):
    context = {'error_message': None}
    __set_context_for_file_selection_enabled(True, context)
    if request.method == 'POST':
        form = DataFileForm(request.POST)
        if form.is_valid():
            file_name = form.cleaned_data['data_file']
            form.fields['data_file'].initial = file_name
            if __read_file_and_load_stats(file_name, context):
                __set_context_for_file_selection_enabled(False, context)
                form.fields['data_file'].disabled = True
            else:
                __set_context_for_file_selection_enabled(True, context)
    context['form'] = form
    return render(request, 'home.html', context)


def train_model(request):
    pass

def __set_context_for_file_selection_enabled(is_enabled, context):
    context['select_btn_disabled'] = '' if is_enabled else 'disabled'
    context['change_btn_disabled'] = 'disabled' if is_enabled else ''
    context['flow_chart_visibility'] = 'invisible' if is_enabled else 'visible'


def __read_file_and_load_stats(file_name, context):
    file_path = os.path.join(settings.BASE_DIR, 'data/' + file_name)
    try:
        data_frame = read_csv(file_path)
        if int(data_frame.shape[1]) < 2: raise Exception("Data file has only one column")
        if int(data_frame.shape[0]) < 2: raise Exception("Data file has only one row")
        if not __has_headers(data_frame): raise Exception("Data file has no headers")
        context['error_message'] = None
        __set_default_flowchart_parameters(file_name, data_frame, context)
        return True
    except Exception as e:
        context['error_message'] = str(e)
        return False


def __has_headers(dataframe):
    for header in dataframe.columns:
        try:
            float(header)
            return False
        except ValueError:
            continue
    return True


def __set_default_flowchart_parameters(file_name, data_frame, context):
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
    context['warning_icon_visibility'] = ""
    context['check_icon_visibility'] = "hidden"
    context['predict_btn_state'] = "disabled"
