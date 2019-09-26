import os
import os.path
from django.shortcuts import render
from pandas import read_csv
from mlflow.forms import DataFileForm
from django.conf import settings


def home_view(request):
    context = {'error_message': None}
    __set_context_for_file_selection_enabled(True, context)
    if request.method == 'POST':
        form = DataFileForm(request.POST)
        context["post_context"] = form.is_valid()
        if form.is_valid():
            file_name = form.cleaned_data['data_file']
            form.fields['data_file'].initial = file_name
            if __read_file_and_load_stats(file_name, context):
                __set_context_for_file_selection_enabled(False, context)
                form.fields['data_file'].disabled = True
            else:
                __set_context_for_file_selection_enabled(True, context)
    else:
        form = DataFileForm()
    context['form'] = form
    return render(request, 'home.html', context)


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
        context['data_file_rows'] = int(data_frame.shape[0])
        context['data_file_cols'] = int(data_frame.shape[1])
        context['data_file_name'] = file_name
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
