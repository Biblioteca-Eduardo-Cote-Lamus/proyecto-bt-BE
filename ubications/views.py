from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .consts import SCHEDULE_HOURS
from .models import Ubication, HourSchedule
from django.db import transaction
from .serializers import UbicationSerializer

@api_view(['POST'])
def create_ubication(request):
    try:
        data = request.data.get('data')
        required_fields = ['name', 'totalBecas', 'managerId', 'isOfficeSchedule']
        for field in required_fields:
            if field not in data:
                return Response({"message": f"El campo '{field}' es obligatorio"}, status=400)
        #extract the data
        with transaction.atomic():
            ubication = Ubication.objects.create(
                name=data['name'],
                total_becas=data['totalBecas'],
                manager_id=data['managerId'],
                is_schedule_office=data['isOfficeSchedule']
            )
            if not ubication.is_schedule_office:
                schedule_hours = data.get('schedule', [])
                hours_ids = HourSchedule.objects.filter(tiempo__in=schedule_hours).values_list('id', flat=True)
                ubication.schedule.add(*hours_ids)
        return Response({"message": "Se ha agregado la nueva ubicacion"}, status=200)
    except Exception as e:
        return Response({"message": str(e)}, status=500)
    
@api_view(['GET'])
def list_ubications(request): 
    try:
        response = UbicationSerializer(Ubication.objects.all(), many=True)
        return Response({
            "ubications": response.data
        })
    except Exception as e:
       return Response({"message": str(e)}, status=500)


