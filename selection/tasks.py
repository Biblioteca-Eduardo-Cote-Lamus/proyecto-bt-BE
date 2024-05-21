from celery import shared_task
from .models import BecaTrabajo
from .helpers import AssignUbication, SelectionConst, AssignStatistics
from ubications.models import AssignationBecas, Schedule, Ubication
from django.db.models import Q
from dotenv import load_dotenv
import os
from datetime import datetime

@shared_task
def asign_ubication_task( beca_id: str ):
    """
        Tarea asincrona encarga de manejar la asignacion de ubicacion a una beca.
    Args:
        beca_id (int): Llave primaria del beca a realizar la asignacion de ubicacion.
    """
    try: 
        # buscamos al beca y obtenemos su horario 
        beca = BecaTrabajo.objects.get(code=beca_id)

        # verificamos primero que el beca no tenga asignaciones ya realizadas
        if beca.assignations.all().count() > 0:
            write_log(f"El beca {beca.code} ya tiene asignaciones realizadas.", "INFO")
            return "El beca ya fue asignado a una ubicacion en el proceso de seleccion."
        
        # Ejecutamos las funciones necesarias de la clase AssignUbication para obtener la ubicacion y persistir en la base de datos
        info, ubication = AssignUbication().assign_random_ubication(beca.schedule)

        # en caso de que se logre asignar una ubicacion se persiste en la base de datos
        if info is not None and ubication is not None:
            
            # obtenemos los ids de los horarios de la ubicacion
            schedules_id = get_schedules_by_type_schedule(ubication, info)

            # obtenemos los objetos de tipo AssignationBecas
            assignations = get_assignations_objs(info, schedules_id, beca.pk)
            
            # Usando bulk_create para insertar todos los objetos en la base de datos
            AssignationBecas.objects.bulk_create(assignations)

            write_log(f"Se asigno la ubicacion {ubication.name} al beca {beca.code}. Ids de los horarios asginados {str(schedules_id)}. Beca {info['beca']}", "SUCCESS")

            return "Ubicacion asignada correctamente."

        write_log(f"No se pudo asignar una ubicacion al beca {beca.code}.", "ERROR")
        
        return "El estudiante no se ajusta a ningun horario de ninguna ubicacion."
    except Exception as e:
        write_log(f"Error al asignar la ubicacion al beca {beca_id}. Error: {str(e)}", "ERROR")
        return "Error al asignar la ubicacion."


def get_schedules_by_type_schedule(ubication: Ubication, info: AssignStatistics.AssignStatisticsResponse) ->  list[int]:
    """Funcion que obtienes la lista de id de horarios dada la ubicacion y la informacion de estadisticas del beca.

    Args:
        ubication (Ubication): ubicacion a la que pertenencen los horarios
        info (AssignStatiticsResponse): informacion de estadisticas del beca

    Returns:
        list[int]: lista de id de horarios
    """
    # si el tipo de horario de la ubicacion es custom, debemos obtener los horarios donde se incluya al beca 
    if ubication.schedule_type.name == SelectionConst.SCHEDULE_TYPES['custom']:
        schedules_id = Schedule.objects.filter(Q(ubication_id=ubication.pk) &  Q(becas_json__contains=[{'name': info['beca']}])).values_list('id', flat=True)
    # si son del tipo unificado, solo obtenemo las horas de inicio y fin y la ubicacion para obtener los horarios
    else:
        schedules_id = Schedule.objects.filter(
            ubication_id=ubication.id ,
            start_hour = info['schedule_info']['hours'][0]['start'] ,
            end_hour = info['schedule_info']['hours'][0]['end'] ,
        ).values_list('id', flat=True)
    return schedules_id

def get_assignations_objs(info, schedules_ids, beca_id) -> list[AssignationBecas]:
    """Funcion que retorna una lista de objetos de tipo AssignationBecas dado la informacion del beca y los ids de los horarios.

    Args:
        info (AssignStatiticsResponse): informacion de estadisticas del beca
        schedules_ids (lists[int]): lista de ids de horarios
        beca_id (int): id del beca

    Returns:
        list[AssignationBecas]: Lista de objetos de tipo AssignationBecas
    """
    if info['preselected']:
        status = SelectionConst.STATUS_ASSIGNATION['preselected']
    
    if not info['preselected'] and ( info['percentageDaysCovered'] >= 60 or info['percentageHoursCovered'] >= 60 ):
        status = SelectionConst.STATUS_ASSIGNATION['candidate']
    
    return [
        AssignationBecas(beca_id=beca_id, schedule_id=schedule_id, status=status) 
        for schedule_id in schedules_ids
    ]

def write_log(message: str, stateful: str):
    # cargamos las variables de entorno
    load_dotenv()
    path_logs = os.getenv('ASSIGNATION_PATH_LOGS')
    with open(path_logs, 'a') as file:
        # agregar la fecha y hora al mensaje
        time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        file.write(f'[ {time} ] {stateful}: {message} \n')