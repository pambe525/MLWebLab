from django.shortcuts import render
from mlflow.helpers import get_context
from mlflow.helpers import set_file_selection_context
from mlflow.helpers import read_csv_datafile
from mlflow.helpers import set_control_panel_context
from mlflow.forms import ControlPanelForm


def home_view(request):
    context = get_context(request)
    context["control_form"] = ControlPanelForm()
    # if context["datafile_form"].is_valid() and "select_btn" in request.POST.keys():
    #     context["control_form"].fields["data_file_name"].initial = context["data_file_name"]
    # elif "train_btn" in request.POST.keys():
    #     context["answer"] = request.POST
    #     file_name = request.POST["data_file_name"]
    #     context["datafile_form"].fields["data_file"].initial = request.POST["data_file_name"]
    #     set_file_selection_context(context, context["datafile_form"], False)
    #     try:
    #         data_frame = read_csv_datafile(file_name)
    #         set_default_container_context(context, file_name, data_frame)
    #         context["training_score"] = 0.57
    #         context["validation_score"] = 0.47
    #         context["active_tab"] = "validate"
    #         context["validation_disabled"] = False
    #     except Exception as e:
    #         context["error_message"] = str(e)
    return render(request, 'home.html', context)

