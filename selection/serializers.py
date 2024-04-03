from rest_framework import serializers
from .models import  SelectionState

class SelectionStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectionState
        fields = "__all__"