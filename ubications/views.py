from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .consts import SCHEDULE_TYPES
from .models import Ubication, HourSchedule
from django.db import transaction
from .serializers import UbicationSerializer, ManagerSerializer
from django.contrib.auth import get_user_model
import json

@api_view(['POST'])
def create_ubication(request):
    try:
        data = json.loads(request.data['ubication'])
        photo = request.FILES.get('photo')
        required_fields = ['ubication', 'becas', 'manager', 'typeSchedule', 'schedule', 'description']
        for field in required_fields:
            if field not in data.keys():
                return Response({"message": f"El campo '{field}' es obligatorio"}, status=400)
        
        # mime type permits only image/* files
        if not photo.content_type.startswith('image/'):
            return Response({"message": "El archivo no es una imagen."}, status=400)
        if not photo:
            return Response({"message": "La imagen del lugar es obligatoria."}, status=400)
        #extract the data
        with transaction.atomic():
            ubication = Ubication.objects.create(
                name=data['ubication'],
                manager_id=data['manager'],
                total_becas=data['becas'],
                is_schedule_office= True if data['typeSchedule'] == SCHEDULE_TYPES[1] else False,
                description=data['description'],
                img=photo
            )
            if not ubication.is_schedule_office:
                schedule_hours = data['schedule']
                hours_ids = HourSchedule.objects.filter(tiempo__in=schedule_hours).values_list('id', flat=True)
                ubication.schedule.add(*hours_ids)
        return Response({"message": "Se ha agregado la nueva ubicacion"}, status=200)
    except Exception as e:
        return Response({"message": "Ha ocurrido un error inesperado. Si el problema persiste, comuniquese con soporte."}, status=500)
    
@api_view(['GET'])
def list_ubications(request): 
    try:
        response = UbicationSerializer(Ubication.objects.all(), many=True)
        return Response({
            "ubications": response.data
        })
    except Exception as e:
       return Response({"message": str(e)}, status=500)


@api_view(['GET'])
def list_managers(request):
    try:

        manager_list = ManagerSerializer(
            get_user_model().objects.filter(rol_id=2), 
            many=True
        )

        return Response({"ok": True, "data": manager_list.data}, status=200)
    
    except Exception as e:
        return Response({"message": str(e)}, status=500)


