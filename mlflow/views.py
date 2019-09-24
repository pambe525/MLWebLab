import os
from django.shortcuts import render
from mlflow.forms import DataFileForm
from pandas import read_csv


def home_view(request):
    context = {}
    _set_context_for_file_selection_enabled(True, context)
    if request.method == 'POST':
        form = DataFileForm(request.POST)
        if form.is_valid() and form.cleaned_data['data_file'] != form.fields['data_file'].initial:
            file_name = form.cleaned_data['data_file']
            form.fields['data_file'].initial = file_name
            form.fields['data_file'].disabled = True
            context['data_file_name'] = file_name
            if _read_file_and_load_stats(file_name, context):
                _set_context_for_file_selection_enabled(False, context)
    else:
        form = DataFileForm()

    context['form'] = form
    return render(request, 'home.html', context)


def _read_file_and_load_stats(file_name, context):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(BASE_DIR, 'data/' + file_name)
    try:
        data_frame = read_csv(file_path)
        context['error_message'] = None
        context['data_file_rows'] = int(data_frame.shape[0])
        context['data_file_cols'] = int(data_frame.shape[1])
        return True
    except Exception as e:
        context['error_message'] = str(e)
        return False


def _set_context_for_file_selection_enabled(is_enabled, context):
    context['select_btn_disabled'] = '' if is_enabled else 'disabled'
    context['change_btn_disabled'] = 'disabled' if is_enabled else ''
    context['flow_chart_visibility'] = 'invisible' if is_enabled else 'visible'
