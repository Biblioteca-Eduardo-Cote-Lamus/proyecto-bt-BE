from   ubications.models import Ubication
from django.conf import settings
import random 
import tabula as tb
import numpy as np


__schedule_types = {
    "unifiedWithoutSaturday": 'unifiedWithoutSaturday',
    "unifiedIncludingSaturday": 'unifiedIncludingSaturday',
    "custom": 'custom',

}


def __free_schedule_hours(schedule):
    """
        Funcion que determina el horario a asginar la beca si el tipo de horario es de oficina

    Args:
        schedule (File): Documento en formato pdf correspondiente al horario del beca.

    Returns:
        tuple: Una tupla con dos valores: dict y dict
        0 -> tiene la informacion de las horas totales y porcentaje de cumplimiento en horario de oficina {'total', 'total_percentage'}
        1 -> informacion de los horarios de disponibiliad por dia 
    """

    # dias de la semana 
    days = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado']

    # horario de atencion de la biblioteca en horario de oficina. Se incluye hasta las 8pm
    library_schedule = [
        '06:00-07:00',
        '07:00-08:00',
        '08:00-09:00',
        '09:00-10:00',
        '10:00-11:00',
        '11:00-12:00',
        '12:00-13:00',
        '13:00-14:00',
        '14:00-15:00',
        '15:00-16:00',
        '16:00-17:00',
        '17:00-18:00',
        '18:00-19:00',
        '19:00-20:00',
    ]


    # leemos el pdf del horario.
    schudule_pdf = tb.read_pdf(schedule, lattice=True, pages='all', encoding='latin-1')

    # diccionario para determinar las horas libres por cada dia.
    free_schedule_by_day = {
        'lunes': [],
        'martes': [],
        'miercoles': [],
        'jueves': [],
        'viernes': [],
        'sabado': []
    }

    # calcula la cantidad de horas totales disponibles 
    free_hours = { "total": 0, "total_percentage": 0 }

    # para cada fila de los valores del horario se hara lo siguiente
    # Aclarcion: es horario[1].values debido a que el documento cuenta con dos tablas. La segunda tabla corresponde al horario
    # Aclaracion 2: Cada fila corresponde a una franja horario del horario, es decir, 06:00-07:00, por lo tanto, row almacena toda la informacion 
    # de la franja horario y la informacion por cada dia hasta el sabado. En caso de que en esa franja no tenga clase, se pondra un ., sino, el nombre de la materia. 
    # Por ejemplo, se veria algo asi [' 06:00-07:00', '.', 'materia x', 'materia x2' ... ,'.'] -> esto quiere decir que para el horario de 6am a 7am, para el lunes no tiene nada, para el martes
    # tiene una clase, para el miercoles igual y asi sucesivamente. 
    for row in schudule_pdf[1].values:
        # obtenemos el indice y el valor para cada dato de la franja -> 0: franja horario, 1:Lunes, 2:Martes, ..., 7:Sabado
        for index, value in enumerate(row):
            # no tenemos en cuenta la franaja horaria.
            if index == 0:
                continue 
            # si leemos un . es que tiene libre 
            if value == '.' and row[0] in library_schedule :
                # por tanto. al diccionario, para ese dia, agregamos la franja horario que siempre se encuentra en la posicion 0 
                free_schedule_by_day[days[index - 1]].append(row[0])
                free_hours['total'] += 1

    free_hours['total_percentage'] = (free_hours['total']*100)/(len(library_schedule)*6)

    return (free_hours, free_schedule_by_day)


def assign_random_ubication(schedule):
    """
        Utilidad que determina la ubicacion a asignar al beca.
    Args:
        schedule (File): Corresponde al horario en formato pdf del beca.
    """

    # Determine las horas de disponibilidad del beca para cada dia de la semana entre las 6AM y 8PM 
    free_hours = __free_schedule_hours(schedule) 

    # gurdamos las ubicaciones ya comprobadas
    checked_ubication = set()

    # obtenemos todas las ubicaciones
    allubications = Ubication.objects.all()

    # En tal caso de si en la ubicacion que se escogio, no cumpla con ninguno de los horarios, se seguira buscando
    while len(checked_ubication) != Ubication.objects.count():
        # Seleccione una ubicacion de manera aleatoria
        ubication = random.choice(allubications)

        # verficamos si la ubicacion ya fue comprobada
        if ubication.id in checked_ubication:
            continue
        
        checked_ubication.add(ubication.id)

        
        if ubication.schedule_type.name == __schedule_types['unifiedWithoutSaturday'] or ubication.schedule_type.name == __schedule_types['unifiedIncludingSaturday']:
            beca_schedule_info = assign_in_unified_schedule(
                schedule=ubication.schedule_format.schedule,
                student_schedule=free_hours[1]
            )

        if ubication.schedule_type.name == __schedule_types['custom']:
            pass

        # Si el beca cumple con al menos un horario de la ubicacion, entonces se preselecciona y se finaliza el proceso, en caso contrario, se sigue buscando
        if isinstance(beca_schedule_info, dict):
            # liberamos todos los recursos usados
            del checked_ubication
            del free_hours

            return beca_schedule_info, ubication
        
    # liberamos todos los recursos usados 
    del checked_ubication
    del free_hours
    return None, None

#  Funcion que determina si el estudiante cumple con el horario de la ubicacion si el tipo de horario es de unificado
def assign_in_unified_schedule(*,schedule, student_schedule):
    """
    Funcion que determina si el estudiante cumple con el horario de la ubicacion.

    Args:
        schedule (json): Horario de la ubicacion. Se obtiene del modelo ShecduleFormat
        student_schedule (list<dict>): Horario del estudiante. Se obtiene apartir del horario pdf del estudiante.

    Returns:
        tuple: Una tupla con dos valores: bool y str
        0 -> True si el estudiante cumple con el horario de la ubicacion, False en caso contrario
        1 -> 'preselected' si el estudiante cumple con todas las horas de la ubicacion, 'candidate' si cumple con al menos el 60% de las horas de la ubicacion, 'not candidate' en caso contrario
    """

    selected_schedule = set()

    schedule_data = schedule['schedule']

    while len(selected_schedule) != len(schedule_data):
        # seleccionamos un horario de manera aleatoria, en este caso manejamos el indice para no seleccionar el mismo horario
        index = random.randint(0, len(schedule_data) - 1)
        
        if index in selected_schedule:
            continue
        
        selected_schedule.add(index)

        selected_hours = set()

        while len(selected_hours) != len(schedule_data[index]['hours']):
            # seleccionamos un horario de manera aleatoria, en este caso manejamos el indice para no seleccionar el mismo horario
            index_hour = random.randint(0, len(schedule_data[index]['hours']) - 1)
            
            if index_hour in selected_hours:
                continue
            
            selected_hours.add(index_hour)

            hora = schedule_data[index]['hours'][index_hour]

            start, end = hora['start'], hora['end']

            if  'sabado' not in schedule_data[index]['days'] and len(schedule_data[index]['days']) == 5: 
                schedule_student = list(student_schedule.values())[0:-1]
            elif 'sabado' in schedule_data[index]['days'] and len(schedule_data[index]['days']) == 6:
                schedule_student = list(student_schedule.values())
            else:
                schedule_student = list(student_schedule.values())[-1]
            
            schedule_student_data = __verify_schedule_student(subschedule=schedule['scheduleFormat2'][index][index_hour], 
                                                                  schedule_s=schedule_student, 
                                                                  total_days=len(schedule_data[index]['days']))


            if schedule_student_data['preslected'] or schedule_student_data['days_percentage'] >= 60:
                schedule_student_data['schedule_info'] = {"start": start, "end": end} 
                # liberamos todos los recursos usados 
                del selected_schedule
                del selected_hours
                return schedule_student_data
    # liberamos todos los recursos usados
    del selected_schedule
    del selected_hours
    return {
        'days_percentage': 0,
        'preslected': False,
        'total_days_can': 0,
        'days_cumpliment': []
    }


def assign_custom_ubication(*, schedule, student_schedule):

    def get_index_day(day):
        if day == 'lunes':
            return 0
        if day == 'martes':
            return 1
        if day == 'miercoles':
            return 2
        if day == 'jueves':
            return 3
        if day == 'viernes':
            return 4
        if day == 'sabado':
            return 5

    # lo primero es obtener los horarios asignado al beca 
    schedulebybeca = get_schedule_by_beca(schedule=schedule['schedule'])

    selected_becas = set()

    becas_keys = list(schedulebybeca.keys())

    while len(selected_becas) != len(becas_keys):
        # Seleccionamos alguna key (beca) de manera aleatoria
        random_beca = random.choice(becas_keys)

        # del horario de estudiante, extraemos solo los dias que tiene asignado el beca
        indexes_days = [get_index_day(day[0]) for day in schedulebybeca[random_beca]['days']] 
        subschedulestudent = [ list(student_schedule.values())[index] for index in indexes_days ]



        pass

    pass

def get_schedule_by_beca(*, schedule):
    """Funcion que obtiene los horarios asignados a cada beca.

    Args:
        schedule (dict): Horario de la ubicacion. Se obtiene del modelo ScheduleFormat

    Returns:
        dict: Un diccionario con llaves el nombre del beca (beca 1, beca 2, etc) y como valor un diccionario con la informacion de los dias y horas asignadas al  beca.
        Ejemplo:
                {
                   ...,
                    "Beca 1": {
                        "hours": [
                            {
                                "start": "08:00 AM",
                                "end": "12:00 PM"
                            },
                            {
                                "start": "08:00 AM",
                                "end": "10:00 AM"
                            },
                            {
                                "start": "08:00 AM",
                                "end": "12:00 PM"
                            }
                        ],
                        "days": [
                            [
                                "miercoles",
                                0,
                                1
                            ],
                            [
                                "martes",
                                1,
                                0
                            ],
                            [
                                "lunes",
                                3,
                                0
                            ]
                        ]
                    }
                }
        En la seccion de dias, vienen dos numeros, el primero indica el dia de la semana y el segundo la hora de inicio de la franja horaria. Esto es para buscar en el scheduleFormat2 los horarios de manera mas directa.
    """
    # Diccionario para almacenar las horas asignadas a cada beca
    horarios_por_beca = {}

    # Itera sobre cada entrada en el horario
    for i, entry in enumerate(schedule):
        for j, hour_entry in enumerate(entry["hours"]):
            for beca in hour_entry["becas"]:
                beca_name = beca["name"]
                # Agrega la hora al diccionario, agrupándola por nombre de beca
                if beca_name in horarios_por_beca:
                    if entry["days"][0] not in horarios_por_beca[beca_name]['days'][0]:
                        horarios_por_beca[beca_name]['days'].append((entry["days"][0],i,j))
                    horarios_por_beca[beca_name]['hours'].append({
                        "start": hour_entry["start"],
                        "end": hour_entry["end"],
                    
                    })
                else:
                    horarios_por_beca[beca_name] = {
                            "hours": [
                                {
                                    "start": hour_entry["start"],
                                    "end": hour_entry["end"]
                                }
                            ],
                            "days": [(entry["days"][0],i,j)],
                        }

    return horarios_por_beca

def __verify_schedule_student(*, subschedule, schedule_s, total_days=0):
    """Funcion encargada de verificar si el estudiante cumple con el horario de la ubicacion para cada dia de la semana.

    Args:
        subschedule (list<str>): Sublista de un horario de la ubicacion. Contiene las horas entre hora inicio y hora fin.
        schedule_s (list): Horario del estudiante 
        total_days (int, optional): Indica el total de dias que el estudiante debe de cumplir.

    Returns:
        dict: Un diccionario con la siguiente informacion:
        'days_percentage': Porcentaje de cumplimiento de los dias del estudiante con el horario de la ubicacion
        'preslected': True si el estudiante cumple con todas las horas de la ubicacion, False en caso contrario
        'total_days_can': Total de dias que el estudiante cumple con el horario de la ubicacion,
        'days_cumpliment': Lista de booleanos que indica si el estudiante cumple con el horario de la ubicacion para cada dia de la semana.
    """
    result = []
    total_days_can = 0
    for scheduleday in schedule_s:
        result.append(np.all(np.in1d(subschedule, scheduleday)))
        total_days_can += np.count_nonzero(result[-1])
    return {
        'days_percentage': (total_days_can*100)/total_days,
        'preslected': np.all(result),
        'total_days_can': total_days_can,
        'days_cumpliment': result
    }
