from rest_framework import serializers
from .models import Ubication, HourSchedule
from .consts import SCHEDULE_OFFICE_HOURS
from authApi.models import Usuario
class HourScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourSchedule
        fields = ['tiempo']

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
        if obj.is_schedule_office:
           return obj.schedule.filter(tiempo__in=SCHEDULE_OFFICE_HOURS).values_list('tiempo', flat=True)
        return obj.schedule.values_list('tiempo', flat=True)

    class Meta:
        model = Ubication
        fields = ['id', 'name', 'total_becas', 'manager', 'is_schedule_office', 'schedule']


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