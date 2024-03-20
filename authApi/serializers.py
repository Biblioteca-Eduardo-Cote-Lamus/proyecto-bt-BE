from rest_framework import serializers
from .models import Usuario
from rest_framework_simplejwt.tokens import RefreshToken
from .util.generateTokens import  get_tokens_for_user

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "email", "first_name", "last_name", "is_active"]

class LoginSuccessSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    def get_user(self, obj):
        return UserSerializer(obj["user"]).data

    def get_token(self, obj):
        return get_tokens_for_user(obj["user"])
