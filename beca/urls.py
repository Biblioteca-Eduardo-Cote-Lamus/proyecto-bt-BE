from django.urls import path
from beca.views import BecaList

urlpatterns = [
    path('', BecaList.as_view(), name='beca-list'),
]