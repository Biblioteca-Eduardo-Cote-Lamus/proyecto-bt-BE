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

    #Algoritmo
    # Seleccione una ubicacion de manera aleatoria
    # Determine las horas de disponibilidad del beca para cada dia de la semana 
    # Lea el json correspondiente al horario de la ubicacion y extraiga sus datos relevantes
    # Determine si el beca cumple con el horario de la ubicacion, en tal caso, sera preseleccionado 
    # Si cumple con al menos el 60 o 70% de la disponibilidad de horas, dejelo como un candidato a dicha ubicacion 

    # Determine las horas de disponibilidad del beca para cada dia de la semana entre las 6AM y 8PM 
    free_hours = __free_schedule_hours(schedule) 


    # gurdamos las ubicaciones ya comprobadas
    checked_ubication = set()


    while len(checked_ubication) != Ubication.objects.count():
         # Seleccione una ubicacion de manera aleatoria
        ubication = random.choice(Ubication.objects.all())
        # verficamos si la ubicacion ya fue comprobada
        if ubication.id in checked_ubication:
            continue
        
        checked_ubication.add(ubication.id)

        beca_schedule_info = can_beca_assign_in_ubication(schedule=ubication.schedule_format.schedule,student_schedule=free_hours[1])

        # Si el beca cumple con al menos un horario de la ubicacion, entonces se preselecciona y se finaliza el proceso, en caso contrario, se sigue buscando
        if isinstance(beca_schedule_info, dict):
            # liberamos todos los recursos usados
            del checked_ubication
            del free_hours
            return beca_schedule_info, ubication
    del checked_ubication
    del free_hours
    return None, None


def can_beca_assign_in_ubication(*,schedule, student_schedule):
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
            # generamos el subschedule list para hacer la comprobacion si el estudiante cubre todas esas horas cada dia 

            if  'sabado' not in schedule_data[index]['days'] and len(schedule_data[index]['days']) == 5: 
                subschedule = __get_sub_schedule_list(start=start, end=end, schedule_format=schedule['scheduleFormat'], index=index)
                schedule_student_data = __verify_schedule_student(subschedule=subschedule, 
                                                                  schedule_s= list(student_schedule.values())[0:-1], 
                                                                  total_days=len(schedule_data[index]['days']))
            elif 'sabado' in schedule_data[index]['days'] and len(schedule_data[index]['days']) == 6:
                subschedule = __get_sub_schedule_list(start=start, end=end, schedule_format=schedule['scheduleFormat'], index=index)
                schedule_student_data = __verify_schedule_student(subschedule=subschedule, 
                                                                  schedule_s= list(student_schedule.values()), 
                                                                  total_days=len(schedule_data[index]['days']))
            else:
                schedule_student_data = __verify_schedule_student(subschedule=schedule['scheduleFormat'][index], 
                                                                  schedule_s= [list(student_schedule.values())[-1]], 
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

def __get_sub_schedule_list(*, start, end, schedule_format, index):
    """Funcion que genera una sublista de un horario de la ubicacion.

    Args:
        start (str)): Hora de inicio de la sublista
        end (str): Hora de finalizacion de la sublista
        schedule_format (list<str>): Horario de la ubicacion por cada dia de la semana
        index (int): Indice del horario de la ubicacion

    Returns:
        list: Sublista del horario de la ubicacion
    """
    if 'PM' in start and not start.startswith('12'):
        start = str(int(start.split(':')[0]) + 12) + ':00'
    else :
        start = start.split(':')[0] + ':00'

    if 'PM' in end and not end.startswith('12'):
        end = str(int(end.split(':')[0]) + 12) + ':00'
    else :
        end = end.split(':')[0] + ':00'
        
    # encontramos el indice donde empieza y termina las horas 
    start_index = schedule_format[index].index( next( h for h in  schedule_format[index] if h.startswith(start) )) 
    end_index = schedule_format[index].index( next( h for h in  schedule_format[index] if h.endswith(end) )) 

    # generamos el slice 
    if start_index > end_index:
        return schedule_format[index][ end_index :  start_index ]
    return schedule_format[index][ start_index : end_index ]
