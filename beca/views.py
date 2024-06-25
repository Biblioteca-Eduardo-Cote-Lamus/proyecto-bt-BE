from django.shortcuts import render
from rest_framework import generics
from selection.models import BecaTrabajo, Selection
from .serializers import BecaTrabajoSerializer

class BecaList(generics.ListAPIView):

    serializer_class = BecaTrabajoSerializer
    
    def get_queryset(self):
        current_selection = Selection.objects.last()
        return BecaTrabajo.objects.filter(selection_id=current_selection.pk)