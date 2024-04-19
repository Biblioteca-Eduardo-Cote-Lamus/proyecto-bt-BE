from django.urls import path
from .views import create_ubication, list_ubications


urlpatterns = [
    path('', list_ubications, name="Get all the ubication"),
    path('create-ubication', create_ubication, name="Create a new ubication"),
]