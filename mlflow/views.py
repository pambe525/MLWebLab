from django.http import JsonResponse
from django.shortcuts import render

from mlflow.forms import DataFileForm, ControlPanelForm
from mlflow.helpers import read_csv_datafile, set_data_file_response
from mlflow.methods import fit_linear_regression


def home_view(request):
    response = {"error_message": None, "datafile_form": DataFileForm(),
                "control_form": ControlPanelForm()}
    return render(request, 'home.html', response)


def load_file(request):
    file_name = request.GET.get("data_file")
    response = {'file_name': file_name, 'error_message': None}
    try:
        data_frame = read_csv_datafile(file_name)
        set_data_file_response(response, data_frame)
        request.session['data_frame'] = data_frame.to_json()
    except Exception as e:
        response['error_message'] = str(e)
    return JsonResponse(response)


def train_model(request):
    n_splits = int(request.GET.get('n_splits'))
    response = {"error_message": None}
    json_data = request.session['data_frame']
    try:
        fit_result = fit_linear_regression(json_data, n_splits)
        response.update(fit_result)
    except Exception as e:
        response["error_message"] = str(e)
    return JsonResponse(response)
