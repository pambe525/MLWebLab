from django.shortcuts import render
import os
from os.path import isfile, join

def home_view(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datafiles_path = os.path.join(BASE_DIR, 'data')
    filenames = [f for f in os.listdir(datafiles_path) if isfile(join(datafiles_path, f))]
    context = {"visibility":"invisible", "filenames":filenames}
    return render(request, 'home.html', context)
