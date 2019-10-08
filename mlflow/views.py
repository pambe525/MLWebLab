from django.shortcuts import render
from mlflow.helpers import get_context


def home_view(request):
    context = get_context(request)
    return render(request, 'home.html', context)

