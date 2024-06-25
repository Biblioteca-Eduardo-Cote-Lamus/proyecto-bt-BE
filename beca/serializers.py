from rest_framework import serializers
from selection.models import BecaTrabajo
from collections import defaultdict

#Use this serializer to get the becas of the current selection and their schedules
class BecaTrabajoSerializer(serializers.Serializer):
    """
        Serializer for BecaTrabajo model.
        Use this serializer to get the becas of the current selection and their schedules
        return {
            'beca': {
                'id': int,
                'name': str,
                'last_name': str,
                'ubication': {
                    'id': int,
                    'name': str
                }
            },
            'schedule': {
                'lunes': [
                    {
                        'start': str,
                        'end': str
                    }
                ],
                'martes': [
                    {
                        'start': str,
                        'end': str
                    }
                ],
                'miercoles': [
                    {
                        'start': str,
                        'end': str
                    }
                ],
                'jueves': [
                    {
                        'start': str,
                        'end': str
                    }
                ],
                'viernes': [
                    {
                        'start': str,
                        'end': str
                    }
                ],
                'sabado': [
                    {
                        'start': str,
                        'end': str
                    }
                ]
        }
    """
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
        fields = ['beca' 'schedule']