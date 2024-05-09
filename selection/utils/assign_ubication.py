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


    # Seleccione una ubicacion de manera aleatoria
    ubication = random.choice(Ubication.objects.all())
    # Determine las horas de disponibilidad del beca para cada dia de la semana entre las 6AM y 8PM 
    free_hours = __free_schedule_hours(schedule) 

    # Lea el json correspondiente al horario de la ubicacion y extraiga sus datos relevantes
    with open(f'{settings.MEDIA_ROOT}{ubication.schedule}', 'r') as file:
        schedule_ubication = file
    
    if schedule_ubication['scheduleType'] == __schedule_types['unifiedWithoutSaturday'] :
        pass
   
    if schedule_ubication['scheduleType'] == __schedule_types['unifiedIncludingSaturday'] :
        pass
   
    if schedule_ubication['scheduleType'] == __schedule_types['custom'] :
        pass


def unifiedWithoutSaturday(*,schedule, student_schedule):

    for index, horario in enumerate(schedule['schedule']):
        for hora in horario['hours']:
            # generamos una sublista del schedule_format 
            start, end = hora['start'], hora['end']
            # generamos el subschedule list para hacer la comprobacion si el estudiante cubre todas esas horas cada dia 
            subschedule = __get_sub_schedule_list(start=start, end=end, schedule_format=schedule['schedule_format'], index=index)

            # verificamos si la sublista esta en cada dia del beca. 
            if __verify_schedule_student(schedule_s=student_schedule, subschedule=subschedule):
                return True
            
    return False



def __verify_schedule_student(*, subschedule, schedule_s):
    result = []
    for scheduleday in schedule_s.values():
        result.append(np.all(np.in1d(subschedule, scheduleday)))
    return np.all(result)

def __get_sub_schedule_list(*, start, end, schedule_format, index):
    if 'PM' in start and not start.startswith('12'):
        start = str(int(start.split(':')[0]) + 12) + ':00'

    if 'PM' in end and not end.startswith('12'):
        end = str(int(end.split(':')[0]) + 12) + ':00'

    # encontramos el indice donde empieza y termina las horas 
    start_index = schedule_format[index].index( next( h for h in  schedule_format if h.startswith(start) )) 
    end_index = schedule_format[index].index( next( h for h in  schedule_format if h.endswith(end) )) 

    # generamos el slice 
    return schedule_format[index][ start_index : end_index ]
