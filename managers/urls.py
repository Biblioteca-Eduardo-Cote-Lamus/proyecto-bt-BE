from django.urls import path
from .views import EncargadoListCreateView, EncargadoUpdateDeleteView

urlpatterns = [
    path('', EncargadoListCreateView.as_view(), name="encargado-list-create"),
    path('update/', EncargadoUpdateDeleteView.as_view(), name="encargado-update-delete")
]