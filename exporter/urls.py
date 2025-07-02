from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('export-ecobee/', views.export_ecobee, name='export_ecobee'),
    path('export-odoo-data/', views.export_odoo_data, name='export_odoo_data'),
    path('export-yale-data/', views.export_yale_data, name='export_yale_data'),
]