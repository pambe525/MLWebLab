from django.shortcuts import render

from mlflow.forms import ControlPanelForm
from mlflow.helpers import get_context


def home_view(request):
    context = get_context(request)
    context["control_form"] = ControlPanelForm()
    return render(request, 'home.html', context)

