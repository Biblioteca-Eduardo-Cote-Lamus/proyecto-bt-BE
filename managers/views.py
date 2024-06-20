from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EncargadoCreateSerializer, EncargadoListSerializer, EncargadoUpdateSerializer
from authApi.models import Usuario
from ubications.models import Ubication

from django.contrib.auth.hashers import make_password

# Vista para listar y crear encargados
class EncargadoListCreateView(APIView):

    # Método para listar encargados
    def get(self, request, *args, **kwargs):
        """ 
            Vista para listar encargados registrados en el sistema
        """
        managers = Usuario.objects.filter(rol_id=2)
        serializer = EncargadoListSerializer(managers, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        """
            Vista para crear un encargado en el sistema
        """
        serializer = EncargadoCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Creamos el encargado primero
            manager = Usuario.objects.create(
                id=serializer.data['id'],
                first_name=serializer.data['first_name'],
                last_name=serializer.data['last_name'],
                email=serializer.data['email'],
                rol_id=2,
                password=make_password(serializer.data['password']),
                is_staff=True
            )

            if len(serializer.data['ubications']) != 0:
                # obtenemos las ubicaciones a los que el encargado tendrá acargo y se actualiza
                Ubication.objects.filter(
                    id__in=serializer.data['ubications']
                ).update(manager_id=manager.pk)

            serializerResp = EncargadoListSerializer(manager)

            return Response(serializerResp.data, status=201)
        return Response(serializer.errors, status=400)
    
# Vista para actualizar y eliminar encargados
class EncargadoUpdateDeleteView(APIView):

    # Método para actualizar un encargado
    def put(self, request):
        """
            Vista para actualizar un encargado en el sistema
        """
        try:
            #obtemos los datos enviados desde el cliente
            serializer = EncargadoUpdateSerializer(data=request.data)
            if serializer.is_valid():
                # obtenemos el encargado y actualizamos sus datos
                user = Usuario.objects.filter(pk=serializer.data['id']).get()

                user.first_name = serializer.data['first_name']
                user.last_name = serializer.data['last_name']
                user.email = serializer.data['email']
                if len(serializer.data['password']) != 0:
                    user.password = make_password(serializer.data['password'])
                user.save()

                return Response({
                    "message": "Encargado actualizado correctamente",
                }, status=200)
                 
            return Response(serializer.errors, status=400)
        except Usuario.DoesNotExist:
            return Response({"message": "El usuario no existe"} , status=404)
        except Exception as e:
            return Response({"message": str(e)}, status=500)

    # Método para eliminar un encargado
    def delete(self, request, *args, **kwargs):
        """
            Vista para eliminar un encargado en el sistema
        """
        try:
            # obtenemos el id del encargado a eliminar
            manager_id = request.data.get('id')

            if not manager_id:
                return Response({"message": "El id del encargado es requerido"}, status=400)

            ubications = Ubication.objects.filter(
                manager_id=manager_id
            )

            # sino tiene ubicaciones asignada, se elimina y se retorna un mensaje
            if len(ubications)  == 0:
                Usuario.objects.filter(pk=manager_id).delete()
                return Response({"message": "Encargado eliminado correctamente"}, status=200)
            
            # en caso contrario, se asigna un nuevo encargado a las ubicaciones
            supplier_id = request.data.get('supplier')           
            if not supplier_id:
                return Response({"message": "El id del remplazo es requerido"}, status=400)
            
            ubications.update(manager_id=supplier_id)
            
            Usuario.objects.filter(pk=manager_id).delete()

            return Response({"message": "Encargado eliminado correctamente"}, status=200)
        except Usuario.DoesNotExist:
            return Response({"message": "El usuario no existe"} , status=404)
        except Exception as e:
            return Response({"message": str(e)}, status=500)
