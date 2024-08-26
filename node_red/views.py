
# Create your views here.
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def series_view(request):
    return render(request, 'series.html')
def switch_view(request):
    return render(request,"switch.html")
def button_view(request):
    return render(request,'button.html')
def slider_view(request):
    return render(request,'slider.html')