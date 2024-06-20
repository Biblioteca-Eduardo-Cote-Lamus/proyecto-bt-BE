from django.urls import path
from .views import create_ubication, list_ubications, list_managers, check_total_becas, update_ubication, get_list_ubications_name


urlpatterns = [
    path('', list_ubications, name="Get all the ubication"),
    path('ubications-names', get_list_ubications_name, name="Get all the ubication names"),
    path('create-ubication', create_ubication, name="Create a new ubication"),
    path('update-ubication', update_ubication, name="Update a ubication"),
    path('list-managers', list_managers, name="Get the list of managers in the system"),
    path('check-total-becas',check_total_becas, name="Determina si es posible asignar la cantidad de becas"),
]