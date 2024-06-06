import json
import pandas as pd
import datetime
import csv
import tabula
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Selection, SelectionState, BecaTrabajo
from .serializers import SelectionStateSerializer, BecaTrabajoListForm, AssignationSerializer
from .utils import get_name_and_last_name, make_random_password, left_time
import json
from rest_framework.request import Request
from ubications.models import AssignationBecas, Ubication
from .helpers import AssignStatistics, AssignUbication


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
                        current_state_id = 2
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
    # no staff and no superadmin users
    applicantsSerializer = BecaTrabajoListForm(
       BecaTrabajo.objects.all(), many=True
    )
    return Response({"data": applicantsSerializer.data}, status=200)


@api_view(["GET"])
def check_register_form_state(request):
    current_selection = Selection.objects.last()
    current_date = datetime.datetime.now()

    #return the time left to close the register form 
    time_res = left_time(
        current_selection.register_limit_date.isoformat().split("+")[0], current_date.isoformat()
    )

    # check if the the form is available
    available = current_selection.register_limit_date.timestamp() < current_date.timestamp()

    data = {
        "untilAvailable": current_selection.register_limit_date.date().isoformat(),
        "timeLeft": time_res,
        "available": not available,
    }
    return Response(data, status=200)


@api_view(["GET"])
def check_if_user_can_send_form(request, id: int):
    user = BecaTrabajo.objects.filter(code=id).values()[0]
    current_selection = Selection.objects.last()
    print(user)
    # if the user has not sent the form, the limit date has not passed and the selection process is active, thats means the user can send the form
    if  not user['sended_form'] and (datetime.datetime.now().timestamp() < current_selection.register_limit_date.timestamp()) and (current_selection.active):
        return Response(
            {"message": "User can send form", "canSend": True, "code": 1}, status=200
        )

    # if the user has sent the form, the limit date has not passed and the selection process is active, thats means the user has already submitted the form
    if  user['sended_form'] and (datetime.datetime.now().timestamp() < current_selection.register_limit_date.timestamp()) and (current_selection.active):
        return Response(
            {
                "message": "User has already submitted the form",
                "canSend": False,
                "code": 2,
            },
            status=200,
        )

    # if the user has not sent the form, the limit date has passed and the selection process is active, thats means the user can't send the form
    return Response(
        {"message": "User can't send form, time is over", "canSend": False, "code": 3},
        status=200,
    )


@api_view(["POST"])
def check_schedule_file(request):
    schedule_file = request.FILES.get("schedule")

    if schedule_file.content_type != 'application/pdf':
        return Response(
            {"message": "Solo se aceptan archivos pdf"}, status=400
        )

    pdf = tabula.read_pdf(schedule_file, lattice=True, pages="all",encoding='latin-1')

    schedule_column_format = [
        "Hora",
        "Lunes",
        "Martes",
        "Miercoles",
        "Jueves",
        "Viernes",
        "Sabado",
    ]
    schedule_hour_row_values = [
        "06:00-07:00",
        "07:00-08:00",
        "08:00-09:00",
        "09:00-10:00",
        "10:00-11:00",
        "11:00-12:00",
        "12:00-13:00",
        "13:00-14:00",
        "14:00-15:00",
        "15:00-16:00",
        "16:00-17:00",
        "17:00-18:00",
        "18:00-19:00",
        "19:00-20:00",
        "20:00-21:00",
        "21:00-22:00",
    ]

    if len(pdf) > 2 or len(pdf) == 0:
        return Response(
            {"message": "El número de tablas no corresponde al reporte."}, status=400
        )

    # check if the first table has the correct format
    if not (pdf[0].columns[0] == "Código:" and pdf[0].columns[2] == "Nombre:"):
        return Response(
            {"message": "El formato del reporte no es correcto."}, status=400
        )

    for i in range(len(pdf[1].columns)):
        if pdf[1].columns[i] != schedule_column_format[i]:
            return Response(
                {"message": "El formato del reporte no es correcto."}, status=400
            )
    
    schedule_row_index = 0
    for schedule in pdf[1].values:
        for value in schedule:
            if value != schedule_hour_row_values[schedule_row_index]:
                return Response(
                {"message": "El formato del reporte no es correcto."}, status=400
            )
            break
        schedule_row_index += 1

    return Response({"message": "El formato del reporte es el correcto", "ok": True}, status=200)


"""Funcion que recibe el formulario de registro del beca.

Returns:
    Response: respuesta con codigo 200 en caso que se  procese de manera exitosa. En cualquiera otro caso, codigo 400 o 500 si se produce una excepcion.
"""
@api_view(["POST"])
def register_user(request):
    photo = request.FILES.get("photo")
    schedule = request.FILES.get("schedule")
    data = json.loads(request.data.get("data"))
    # TODO: Leer el horario del beca y designar a que ubicacion enviarlo. 
    try:
        photo.name = f'{data['id']}.{photo.name.split('.')[-1]}'
        schedule.name = f'{data['id']}.{schedule.name.split('.')[-1]}'
        with transaction.atomic():
            beca = BecaTrabajo.objects.get(code=str(data['id']))
            beca.first_name = data['names']
            beca.last_name = data['last_names']
            beca.birth_date = data['birthday'].split('T')[0]
            beca.address = data['address']
            beca.gender = data['gender']
            beca.career = data['academic']
            beca.photo = photo
            beca.schedule = schedule
            beca.motivation = data['motivation']
            beca.extra_studies  = data['studies']
            beca.sended_form = True
                
            beca.save()

        return Response({ "ok": True, 'message': 'Se ha procesado el formulario de manera exitosa.'}, status=200)   
    except Exception as e:
        print(e.with_traceback())
        return Response({ "ok": False}, status=500)   

@api_view(['GET'])
def get_beca_current_state(request, id):
    try:
        beca = get_user_model().objects.get(id=id).becatrabajo
        return Response({'currentState': beca.current_state_id}, status=200)
    except Exception as e:
        return Response({'msg': str(e)}, status=500)

@api_view(['POST'])
def extend_register_form_date(request):
    try:
        with transaction.atomic():
            date = datetime.datetime.fromisoformat(request.data.get('date')).replace(hour=23, minute=59, second=59, microsecond=59999)
            selection = Selection.objects.last()
            selection.register_limit_date = date
            selection.save()
        return Response({'ok': True, 'msg': 'Fecha actualiza'}, status=200)
    except Exception as e:
        return Response({'ok': False, 'msg': str(e)}, status=500)
    
@api_view(['GET'])
def confirm_list_step2(request):
    try:
        with transaction.atomic():
            selection = Selection.objects.filter(active=True).update(current_state_id=3)  # change the current selection id to state 3 (preseleccion)
            # all becatrabajos who submitted registration form, update status also
            BecaTrabajo.objects.filter(sended_form=True).update(current_state_id=3)
        return Response({'ok': True, 'msg': 'Se ha actualizado el estado actual del proceso de seleccion'}, status=200)
    except Exception as e:
        return Response({'ok': False, 'msg': str(e)}, status=500)


@api_view(['GET'])
def get_becas_by_ubication(request: Request):
    """
        Vista para obtener los becas candidatos y preseleccionados por ubicacion
    Returns:
        _type_: _description_
    """
    try:
        # get the ubication id from the query params
        ubication_id = request.query_params.get('ubicationId')
    
        # Obtener la ubicación por su id
        ubication = Ubication.objects.get(id=ubication_id)

        # Obtener todas las asignaciones de becas a través de los horarios de la ubicación usando select_related y prefetch_related
        assignations = AssignationBecas.objects.filter(schedule__ubication=ubication).select_related('beca', 'schedule').values(
            'status', 
            'percentage',
            'notified',
            'beca__code', 
            'beca__first_name', 
            'beca__last_name', 
            'beca__email', 
            'beca__photo', 
            'beca__address',
            'beca__gender',
            'beca__career',
            'beca__extra_studies',
            'beca__motivation',
        ).distinct()

        becasserializer = AssignationSerializer(data=assignations, many=True)
        becasserializer.is_valid()

        return Response({'ok': True, 'becas': becasserializer.data}, status=200)        
    except Exception as e:
        return Response({'msg': str(e)}, status=500)

@api_view(['POST'])
def notify_becas(request):
    """
        Vista para notificar a los becas seleccionados al correo electrónico.
    Returns:
        _type_: _description_
    """
    try:  
        # TODO: Implementar la notificación por correo electrónico

        ids_list = request.data.get('becasIds', [])

        if(len(ids_list) == 0):
            return Response({'ok': False, 'msg': 'No se ha seleccionado ningun beca.'}, status=400)
        
        AssignationBecas.objects.filter(beca_id__in=ids_list).update(notified=True)

        return Response(
            {'ok': True, 'msg': 'Se ha notificado a los becas seleccionados.'}, 
            status=200
        )
    
    except Exception as e:
        return Response({'msg': str(e)}, status=500)

@api_view(['GET'])
def get_list_notified_becas(request):
    """
        Metodo para obtener la lista de becas notificados.
    """
    try:
        assignations = AssignationBecas.objects.select_related('beca', 'schedule').values(
            'status', 
            'percentage',
            'notified',
            'beca__code', 
            'beca__first_name', 
            'beca__last_name', 
            'beca__email', 
            'beca__photo', 
            'beca__address',
            'beca__gender',
            'beca__career',
            'beca__extra_studies',
            'beca__motivation',
        ).distinct().filter(notified=True)

        becasserializer = AssignationSerializer(data=assignations, many=True)
        becasserializer.is_valid()

        return Response({'ok': True, 'becas': becasserializer.data}, status=200)  
    except Exception as e:
        return Response({'msg': str(e)}, status=500)
    
@api_view(['GET'])
def statistic_by_beca(request):
    """
        Funcion para obtener las estadistica de un beca especifico.
    """
    try:
        beca_id = request.query_params.get('becaId')

        assignations = AssignationBecas.objects.filter(beca_id=beca_id).select_related('schedule__ubication')

        statistic = AssignStatistics.get_statistics_by_assignation(assignations=assignations)
        
        return Response({'ok': True, 'data': statistic}, status=200)

    except Exception as e:
        e.with_traceback()
        return Response({'msg': str(e)}, status=500)




@api_view(['GET'])
def ubication_assign(request):

    beca = BecaTrabajo.objects.get(code=1152069)

    res = AssignUbication().assign_random_ubication(beca.schedule)

    res[0]['ubication'] = {
        'name': res[1].name,
    }
    
    return Response({'ok': True, "data": res[0]}, status=200)