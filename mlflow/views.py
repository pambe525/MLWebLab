from django.shortcuts import render

from mlflow.forms import ControlPanelForm
from mlflow.helpers import get_context

from django.http import JsonResponse
from pandas import read_json
from mlflow.methods import fit_linear_regression


def home_view(request):
    context = get_context(request)
    context["control_form"] = ControlPanelForm()
    return render(request, 'home.html', context)


def train_model(request):
    training_ratio = float(request.GET.get('training_ratio'))
    file_name = request.session['datafile']
    response = {'file_name': file_name, 'error_message': "None"}
    data_frame = read_json(request.session['dataframe'])
    try:
        fit_result = fit_linear_regression(data_frame, training_ratio)
        response.update(fit_result)
    except Exception as e:
        response["error_message"] = str(e)
    return JsonResponse(response)
