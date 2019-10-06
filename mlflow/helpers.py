import os
import os.path
from django.shortcuts import render
from pandas import read_csv
from mlflow.forms import DataFileForm
from django.conf import settings


# HomeView Context Manager to manage all page variables and state
class ContextManager:

    def __init__(self, request):
        self.context = {}
        self.data_frame = None

        if not request.POST:
            pass
        elif form.is_valid():
            context = {'error_message': None}
            __set_context_for_file_selection_enabled(True, context)
            # context['post_data'] = request.POST
            if request.method == 'POST':
                form = DataFileForm(request.POST)
                if form.is_valid():
                    datafile_selected(form, context)
            else:
                form = DataFileForm()
            context['form'] = form
            return render(request, 'flowchart.html', context)

    def get_data_frame(self):
        return self.data_frame
