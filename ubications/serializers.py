from rest_framework import serializers
from django.conf import settings
from .models import Ubication
from .consts import SCHEDULE_OFFICE_HOURS
from authApi.models import Usuario
from .utils import schedule_formart
from collections import defaultdict
import json


class UbicationSerializer(serializers.ModelSerializer):
    # Define un campo para el nombre del encargado
    manager = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()

    def get_manager(self, obj):
        # Combinar el nombre y apellido del gerente en un solo campo
        if obj.manager:
            return {"name": f"{obj.manager.first_name} {obj.manager.last_name}", 'photo': None}
        return None
    
    def get_schedule(self, obj):
        # Obtener los horarios de la ubicacion y convertirlos en un diccionario con "scheduleType" y "schedule" como keys
        return obj.schedule_format.schedule
        
        

    class Meta:
        model = Ubication
        fields = ['id', 'name', 'total_becas', 'manager',  'schedule', 'img', 'description']


class ManagerSerializer(serializers.ModelSerializer):

    fullName = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    def get_fullName(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    def get_photo(self, obj):
        return None
    class Meta:
        model = Usuario
        fields = ['id', 'fullName', 'photo']