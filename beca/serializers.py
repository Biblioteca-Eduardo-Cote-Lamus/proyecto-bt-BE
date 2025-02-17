from rest_framework import serializers
from .models import Beca
from collections import defaultdict

class BecaTrabajoSerializer(serializers.Serializer):
    beca = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()

    def get_beca(self, obj):
        return {
            'id': int(obj.code),
            'name': obj.first_name,
            'last_name': obj.last_name,
            'photo': obj.photo.url if obj.photo else '',
            'ubication':{
                'id': obj.ubication.id,
                'name': obj.ubication.name
            }           
        }
    
    def get_schedule(self, obj):
        schedules = obj.beca_schedules.all()

        schedule_format = {
            'lunes': [],
            'martes': [],
            'miercoles': [],
            'jueves': [],
            'viernes': [],
            'sabado': []
        }

        for schedule in schedules:
            schedule_format[schedule.day].append({
                'start': schedule.start_time,
                'end': schedule.end_time
            })

        return schedule_format

    class Meta:
        fields = ['beca', 'schedule']