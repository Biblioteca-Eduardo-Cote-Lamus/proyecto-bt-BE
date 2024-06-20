from rest_framework import serializers
from authApi.models import Usuario


# Serializador para Listar Encargados
class EncargadoListSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    def get_rol(self, obj):
        return obj.rol.descripcion

    class Meta:
        model = Usuario
        fields = ['id', 'first_name', 'last_name', 'email', 'is_active', 'rol']

# Serializador para Crear un Encargado
class EncargadoCreateSerializer(serializers.ModelSerializer):

    ubications = serializers.ListField()
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Usuario
        fields = ['id', 'first_name', 'last_name' ,'email', 'password',  'ubications']

class EncargadoUpdateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    id = serializers.IntegerField(required=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'first_name', 'last_name' ,'email', 'password']

