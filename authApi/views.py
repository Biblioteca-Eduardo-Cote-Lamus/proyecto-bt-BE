from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from authApi.serializers import LoginSerializer, LoginSuccessSerializer
from .models import Usuario


# Create your views here.
@api_view(["POST"])
def login(request):
    try:
        login_data = LoginSerializer(data=request.data)
        if login_data.is_valid():
            user = authenticate(
                email=login_data.data["email"], password=login_data.data["password"]
            )
            if user is not None:
                Usuario.objects.filter(email=login_data.data["email"]).update(
                    last_login=timezone.now()
                )
                return Response(
                    {
                        "data": LoginSuccessSerializer(
                            {
                                "message": "Login successful",
                                "user": user,
                            }
                        ).data
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
    except Exception as e:
        print(e)
        return Response(
            {"message": "Unexpected error has been occurred"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )