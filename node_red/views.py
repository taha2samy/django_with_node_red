
# Create your views here.
from django.shortcuts import render,HttpResponse
from .models import Device,Element
def test_view(request):
    return render(request,'test.html')
def tester_view(request):
    elment=Element.objects.all()[0]
    return render(request,r'cards\templates\Gauge.html',{'element':elment})