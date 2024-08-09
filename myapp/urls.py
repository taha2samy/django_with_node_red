# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('series/', views.series_view, name='series_view'),
    path('switch/', views.switch_view, name='switch_view'),
    path("button/",views.button_view,name="button_view"),
    path("slider/",views.slider_view,name="slider_view")
]
