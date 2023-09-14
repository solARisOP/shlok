from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def index(request):
    return render(request, 'index.html')

# @csrf_exempt  # Disable CSRF protection for simplicity (not recommended for production)
