from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.

def list_ingredients(request):
    
    return JsonResponse({"message": "listing all gredients available"})