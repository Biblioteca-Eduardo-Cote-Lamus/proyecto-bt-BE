from rest_framework import serializers
from .models import  SelectionState, BecaTrabajo

class SelectionStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectionState
        fields = "__all__"

class BecaTrabajoListForm(serializers.ModelSerializer):

    class Meta:
        model = BecaTrabajo
        fields = ['first_name', 'last_name', 'email', 'photo', 'sended_form']