
# Create your views here.
from django.shortcuts import render,HttpResponse
from .models import Device,Element
def test_view(request):
    return render(request,'test.html')
def tester_view(request):
    
    elements = Element.objects.all().order_by('element_id')

    return render(request,r'cards\templates\test_guage.html',{'elements':elements})