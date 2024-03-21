from rest_framework import serializers
from .models import Usuario
from rest_framework_simplejwt.tokens import RefreshToken
from .util.generateTokens import  get_tokens_for_user

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
class UserSerializer(serializers.ModelSerializer):
    
    rol = serializers.SerializerMethodField()
    
    def get_rol(self, obj):
        if obj.is_superuser and obj.is_staff:
            return {"id":1 , "rol": "Administrador"}
        elif obj.is_staff:
            return {"id":2 , "rol": "Encargado"}
        else:
            return {"id":3, "rol": "Beca"}

    class Meta:
        model = Usuario
        fields = ["id", "email", "first_name", "last_name", "is_active", "rol"]

class LoginSuccessSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    def get_user(self, obj):
        return UserSerializer(obj["user"]).data

    def get_token(self, obj):
        return get_tokens_for_user(obj["user"])
