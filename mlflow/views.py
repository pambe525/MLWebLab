from django.shortcuts import render
from mlflow.forms import DataFileForm


def home_view(request):

    context = {'flow_chart_visibility': 'invisible', 'select_btn_disabled': '', 'change_btn_disabled': 'disabled'}

    if request.method == 'POST':
        form = DataFileForm(request.POST)
        if form.is_valid() and form.cleaned_data['data_file'] != form.fields['data_file'].initial:
            context['select_btn_disabled'] = 'disabled'
            context['change_btn_disabled'] = ''
            context['flow_chart_visibility'] = 'visible'
            form.fields['data_file'].initial = form.cleaned_data['data_file']
            form.fields['data_file'].disabled = True

    else:
        form = DataFileForm()

    context['form'] = form
    return render(request, 'home.html', context)
