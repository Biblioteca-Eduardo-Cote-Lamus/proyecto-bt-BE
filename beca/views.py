from django.shortcuts import render
from rest_framework import generics
from .models import Beca, Selection
from .serializers import BecaTrabajoSerializer

class BecaList(generics.ListAPIView):
    serializer_class = BecaTrabajoSerializer

    def get_queryset(self):
        current_selection = Selection.objects.filter(activo=True).first()
        if current_selection is None:
            return Beca.objects.none()
        return Beca.objects.filter(selection=current_selection)