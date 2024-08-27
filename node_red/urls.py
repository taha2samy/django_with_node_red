# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("",views.test_view,name="test_view"),
    path("api/node_red/",views.MyDataView.as_view())
]
