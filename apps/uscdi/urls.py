from django.urls import path

from .views import export_to_csv, export_to_json, uscdi_index


__author__ = "Alan Viars"
app_name = "uscdi"

urlpatterns = [
    path("", uscdi_index, name="uscdi_index"),
    path("export-to-csv/", export_to_csv, name="export_to_csv"),
    path("export-to-json/", export_to_json, name="export_to_json"),
]
