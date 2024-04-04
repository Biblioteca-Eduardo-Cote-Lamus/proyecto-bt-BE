import pandas as pd
import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Selection, SelectionState
from .serializers import SelectionStateSerializer
from .utils import get_name_and_last_name, make_random_password


@api_view(["GET"])
def get_current_selection_state(request):
    current_selection = SelectionStateSerializer(Selection.objects.last().current_state)
    return Response({"currentState": current_selection.data, "ok": True}, status=200)


@api_view(["POST"])
def confirm_list_of_students(request):
    # check if the selection process is active and in the correct state
    current_selection = Selection.objects.last()
    if not current_selection.active or not current_selection.current_state.id == 1:
        return Response(
            {
                "message": "The selection process is not active or is not in the correct state",
                "ok": False,
            },
            status=400,
        )
    # if the selection process is active and in the correct state, create the users
    # TODO: Implements send emails to the users with their credentials

    data = request.data.get("data")
    Usuario = get_user_model()

    for applicant in data["applicants"]:
        last_name, first_name = get_name_and_last_name(applicant["nombre"])
        if not Usuario.objects.filter(id=applicant["codigo"]).exists():
            user = Usuario.objects.create_user(
                email=applicant["correo"],
                password=make_random_password(special_chars=False, length=12),
                first_name=first_name,
                last_name=last_name,
                id=applicant["codigo"],
            )
            user.save()
    # update the selection state to the next state
    current_selection.current_state = SelectionState.objects.get(id=2)
    current_selection.register_limit_date = datetime.datetime.strptime(
        data["limit"], "%Y-%m-%dT%H:%M:%S.%fZ"
    ).date()
    current_selection.save()
    return Response(
        {"ok": True, "message": "Usuarios creados correctamente"}, status=200
    )


@api_view(["POST"])
def upload_file(request):
    postulantes = request.FILES.get("file")
    if postulantes:
        df = pd.read_excel(postulantes, sheet_name="POSTULADOS")
        postulados = (
            df[df["DEPENDENCIA"] == "DIVISION DE BIBLIOTECA"]
            .sort_values(by="PROMEDIO", ascending=False)
            .to_dict(orient="index")
        )

        res = [student for student in postulados.values()]

        return Response({"data": res}, status=200)

    return Response({"message": "File not uploaded"}, status=400)
