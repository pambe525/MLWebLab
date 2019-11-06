from django.http import JsonResponse
from django.shortcuts import render

from mlflow.forms import ControlPanelForm
from mlflow.helpers import get_context
from mlflow.methods import fit_linear_regression


def home_view(request):
    context = get_context(request)
    context["control_form"] = ControlPanelForm()
    return render(request, 'home.html', context)


def train_model(request):
    n_splits = int(request.GET.get('n_splits'))
    response = {"error_message": "None"}
    json_data = request.session['dataframe']
    try:
        fit_result = fit_linear_regression(json_data, n_splits)
        response.update(fit_result)
    except Exception as e:
        response["error_message"] = str(e)
    return JsonResponse(response)
