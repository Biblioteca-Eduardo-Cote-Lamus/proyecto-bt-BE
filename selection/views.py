import pandas as pd
import datetime
import csv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Selection, SelectionState, BecaTrabajo
from .serializers import SelectionStateSerializer
from .utils import get_name_and_last_name, make_random_password,left_time
from authApi.serializers import UserSerializer


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
    
    try:
        with transaction.atomic():
            for applicant in data["applicants"]:
                last_name, first_name = get_name_and_last_name(applicant["nombre"])
                if not Usuario.objects.filter(id=applicant["codigo"]).exists():
                    password = make_random_password(special_chars=False, length=12)
                    user = Usuario.objects.create_user(
                        email=applicant["correo"],
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        id=applicant["codigo"],
                    )
                    beca = BecaTrabajo.objects.create(
                        code=applicant["codigo"],
                        first_name=first_name,
                        last_name=last_name,
                        email=applicant["correo"],
                        selection=current_selection,
                        student=user,
                    )
                    with open(f"credentials.csv", "a", newline="\n") as f:
                        writer = csv.writer(f)
                        writer.writerow([user.id, user.email, password])
                    user.save()
                    beca.save()

            # update the selection state to the next state
            current_selection.current_state = SelectionState.objects.get(id=2)
            current_selection.register_limit_date = datetime.datetime.strptime(
                data["limit"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).date()
            current_selection.save()
        return Response(
            {"ok": True, "message": "Usuarios creados correctamente"}, status=200
        )
    except Exception as e:
        print(e.with_traceback())
        return Response({"message": str(e), "ok": False}, status=400)

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


@api_view(["GET"])
def get_applicants_list(request):
    User = get_user_model()
    # no staff and no superadmin users
    applicantsSerializer = UserSerializer(
        User.objects.filter(is_staff=False, is_superuser=False), many=True
    )
    return Response({"data": applicantsSerializer.data}, status=200)

@api_view(["GET"])
def check_register_form_state(request):
    current_selection = Selection.objects.last()
    current_date = datetime.datetime.now().isoformat()
    time_res = left_time(current_selection.register_limit_date.isoformat().split("+")[0], current_date)
    data = {
        "untilAvailable": current_selection.register_limit_date.date().isoformat(),
        "timeLeft": time_res,
        "available": current_selection.active,
    }
    return Response(data, status=200)

@api_view(["GET"])
def check_if_user_can_send_form(request, id: int):
    user = BecaTrabajo.objects.filter(code=id).values()[0]
    current_selection = Selection.objects.last()
    
    # if the user has not sent the form, the limit date has not passed and the selection process is active, thats means the user can send the form
    if not all(value for value in user.values()) and datetime.datetime.now().date() < current_selection.register_limit_date.date() and current_selection.active:
        return Response({"message": "User can send form", "canSend": True, "code":1}, status=200)

    # if the user has sent the form, the limit date has not passed and the selection process is active, thats means the user has already submitted the form
    if all(value for value in user.values()) and datetime.datetime.now().date() < current_selection.register_limit_date.date() and current_selection.active:
        return Response({"message": "User has already submitted the form", "canSend": False, "code": 2}, status=400)
    
    # if the user has not sent the form, the limit date has passed and the selection process is active, thats means the user can't send the form
    return Response({"message": "User can't send form, time is over", "canSend": False, "code": 3}, status=400)