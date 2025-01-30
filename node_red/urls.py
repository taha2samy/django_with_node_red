# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("",views.test_view,name="test_view"),
    path("test/",views.tester_view,name="guage_view"),
]
