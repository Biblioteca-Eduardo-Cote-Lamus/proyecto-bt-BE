from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from authApi.serializers import LoginSerializer, LoginSuccessSerializer
from .models import Usuario
from .util.hasRole import get_role

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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hasAccess(request):
    rol = request.GET.get("rol")
    id = request.GET.get("id")
    user = Usuario.objects.get(id=id)
    return Response(
        {"message": get_role(user) == rol},
        status=status.HTTP_200_OK,
    )

