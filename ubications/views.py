import json
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .consts import SCHEDULE_TYPES
from .models import Ubication
from django.db import transaction
from .serializers import UbicationSerializer, ManagerSerializer
from django.contrib.auth import get_user_model
from selection.models import Selection
from django.db.models import Sum
from .utils.verify_schedule import verify_schedule
from django.conf import settings

@api_view(['POST'])
def create_ubication(request):
    """Vista para crear una ubicacion

    Args:
        request: request con los datos de la ubicacion

    Returns:
        Response: Respuesta con el mensaje de exito o error
    """
    try:
        data = json.loads(request.data['ubication'])
        photo = request.FILES.get('photo')
        # verificamos que lleguen los campos obligatorios
        required_fields = ['ubication', 'becas', 'manager', 'schedule', 'description']
        for field in required_fields:
            if field not in data.keys():
                return Response({"message": f"El campo '{field}' es obligatorio"}, status=400)
        
        # Verificamos que la imagen llegue y que realmente sea una imagen
        if not photo:
            return Response({"message": "La imagen del lugar es obligatoria."}, status=400)
        if not photo.content_type.startswith('image/'):
            return Response({"message": "El archivo no es una imagen."}, status=400)
        
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
        
        # Verificamos que la estructura del horario sea correcta
        if not verify_schedule(data['schedule']):
            return Response({"message": "La estructura del horario es incorrecta"}, status=400)
        
        # Si todo sale bien Creamos una transaccion para asegurarnos que si algo falla, no se cree la ubicacion
        with transaction.atomic():
            # Guardamos el json correspondiente al horario de la ubicacion.
            Ubication.objects.create(
                name=data['ubication'],
                manager_id=data['manager'],
                total_becas=data['becas'],
                description=data['description'],
                img=photo,
                schedule=f'{settings.MEDIA_ROOT}ubications/{data["ubication"]}/schedule.json'
            )

            # guardamos el json del horario
            with open(f'{settings.MEDIA_ROOT}/ubications/{data["ubication"]}/schedule.json', 'w') as file:
                json.dump(data['schedule'], file)


        return Response({"message": "Se ha agregado la nueva ubicacion"}, status=200)
    except Exception as e:
        return Response({"message": "Ha ocurrido un error inesperado. Si el problema persiste, comuniquese con soporte.", "error": str(e)}, status=500)
    
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
    
    

