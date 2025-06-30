from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('export-ecobee/', views.export_ecobee, name='export_ecobee'),
]
