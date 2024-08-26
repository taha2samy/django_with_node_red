# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("",views.slider_view,name="test_view")
]
