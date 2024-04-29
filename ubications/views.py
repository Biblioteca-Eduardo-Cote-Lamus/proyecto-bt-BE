import json
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .consts import SCHEDULE_TYPES
from .models import Ubication, HourSchedule
from django.db import transaction
from .serializers import UbicationSerializer, ManagerSerializer
from django.contrib.auth import get_user_model
from selection.models import Selection
from django.db.models import Sum

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
        
        # Validamos que la cantidad de becas que se envia a asignar a la ubicaicon no se sobrepase a lo permitido.
        
        # obtenga el total de becas asiganados para este proceso 
        total_becas_available = Selection.objects.last().total_becas 

        # Sume la cantidad de becas asignados para cada ubicacion registrada 
        total_register_ubication_becas = Ubication.objects.all().aggregate(total=Sum('total_becas'))['total']

        if total_register_ubication_becas is None:
            total_register_ubication_becas = 0

        # sume el total enviado desde el cliente con el total registrado
        total = data['becas'] + total_register_ubication_becas

        # si sobre pasa, lanzar el error. 
        if total > total_becas_available:
            return Response({
                "message": "La cantidad de becas asignados no es permitida. Se sobrepasa",
                "permited": abs(total-total_becas_available),
                "ok": False
            }, status=400)
        
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
    
@api_view(['PATCH'])
def update_ubication(request):
    try:
        data = json.loads(request.data['ubication'])
        photo = request.FILES.get('photo')

        files_to_update = ['manager', 'description', 'id']

        # validamos que no ese envien datos adicionales para actualizar
        for field in data.keys():
            if field not in files_to_update:
                return Response({"message": f" el campo {field} no se puede actualizar"}, status=400)
        
         # validamos que el archivo sea si o si una imagen.
        if not photo.content_type.startswith('image/'):
            return Response({"message": "El archivo no es una imagen."}, status=400)
        
        with transaction.atomic():
            ubication = Ubication.objects.get(id=data['id'])
            ubication.manager_id = data['manager']
            ubication.description = data['description']
            if photo:
                ubication.img = photo
            ubication.save()

        return Response({"message": "Se ha modificado la ubicacion", "ok": True}, status=200)


    except Exception as e:
        return Response({"message": str(e), "ok": False}, status=500)
    
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
    

    """
        Verifica al momento de estar creando o modificando la cantidad de becas asignadas a una ubicacion 
        si es posible tomar ese valor o no
    """
@api_view(['GET'])
def check_total_becas(request):
    try:
        # obtenga el total que se asignara desde el cliente
        client_query = str(request.query_params.get('amount', None))

        print(client_query)

        if client_query is None:
            return  Response({
                "message": "La cantidad es obligatoria. ",
                "ok": False
            }, status=400)
        
        if not client_query.isnumeric():
            return  Response({
                "message": "Parametro desconocido. Solo se aceptan numeros.",
                "ok": False
            }, status=400)
        

        # obtenga el total de becas asiganados para este proceso 
        total_becas_available = Selection.objects.last().total_becas 

        # Sume la cantidad de becas asignados para cada ubicacion registrada 
        total_register_ubication_becas = Ubication.objects.all().aggregate(total=Sum('total_becas'))['total']

        # sume el total enviado desde el cliente con el total registrado
        total = int(client_query) + total_register_ubication_becas
        
        # si es none o si es menor o igual a la cantidad de becas para este proceso, se puede.  
        if total <= total_becas_available:
            return Response({
                "message": "La cantidad es permitida ",
                "ok": True
            }, status=200)
        
        return Response({
                "message": "La cantidad no es permitida. Se sobrepasa",
                "permited": abs(total-total_becas_available),
                "ok": False
            }, status=400)
    except Exception as e:

        return  Response({
            "message": f'{e}',
            "ok": False
        }, status=500)
    
    

