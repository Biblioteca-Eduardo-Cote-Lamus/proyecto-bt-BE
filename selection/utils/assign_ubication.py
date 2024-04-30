from   ubications.models import Ubication
import random 
import tabula as tb

"""
    Utilidad que obtiene una ubicacion de manera aleatoria para asignar al beca
"""
def __assign_random_schedule_type_ubication():
    # Pasos: 
    # 1: Seleccione de manera aleatoria el tipo de horario 
    schedule_type = random.choice(['oficina', 'personalizado'])
    # paso 2: Retornamos true si se obtuvo oficina, false si es personalizado
    return True if schedule_type == 'oficina' else False

def __free_schedule_hours(schedule):
    """
        Funcion que determina el horario a asginar la beca si el tipo de horario es de oficina

    Args:
        schedule (File): Documento en formato pdf correspondiente al horario del beca.

    Returns:
        tuple: Una tupla con dos valores: dict y dict
        0 -> tiene la informacion de las horas totales y porcentaje de cumplimiento {'total', 'total_percentage'}
        1 -> informacion de los horarios de disponibiliad por dia 
    """

    # dias de la semana 
    days = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado']

    # horario de atencion de la biblioteca en horario de oficina. Se incluye hasta las 8pm
    library_schedule = [
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
        'Lunes': [],
        'Martes': [],
        'Miercoles': [],
        'Jueves': [],
        'Viernes': [],
        'Sabado': []
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


def __generate_random_schedule(horarios):
    horarios_seleccionados = {
        'Lunes': [],
        'Martes': [],
        'Miercoles': [],
        'Jueves': [],
        'Viernes': []
    }

    horas_semana = 0

    # Iterar sobre los días restantes
    for dia, horas_disponibles in horarios.items():
        if dia == 'Sabado': break
        # Verificar si hay al menos dos horas disponibles para este día
        if len(horas_disponibles) >= 2:
            # Determinar el número máximo de horas consecutivas disponibles
            num_max_horas_consecutivas = min(4, len(horas_disponibles))
            
            # Calcular el número máximo de horas que se pueden agregar sin exceder el límite semanal
            horas_disponibles_dia = min(11 - horas_semana, num_max_horas_consecutivas)
            if horas_disponibles_dia < 2:
                continue  # Saltar este día si no hay suficientes horas disponibles
            
            # Seleccionar aleatoriamente el número de horas para este día (entre 2 y el máximo de horas disponibles)
            num_horas = random.randint(2, horas_disponibles_dia)
            
            # Seleccionar aleatoriamente el índice inicial del rango de horas
            inicio_rango = random.randint(0, len(horas_disponibles) - num_horas)
            
            # Obtener el rango de horas consecutivas seleccionado
            horas_seleccionadas = horas_disponibles[inicio_rango:inicio_rango + num_horas]
            
            # Agregar las horas seleccionadas al diccionario de horarios
            horarios_seleccionados[dia] = horas_seleccionadas
            
            # Actualizar el total de horas de la semana
            horas_semana += num_horas
    
    return horarios_seleccionados


def assign_random_ubication(schedule):
    """Utilidada que determina la ubicacion a asignar al beca.

    Args:
        schedule (File): Corresponde al horario en formato pdf del beca.
    """
    # obtenga el tipo de horario
    schedule_type = __assign_random_schedule_type_ubication()
    # obtenga las ubicaciones que tienen el tipo de horario seleccionado. 
    ubication = random.choice(Ubication.objects.filter(is_schedule_office = schedule_type))


    # si es horario de oficina
    if schedule_type  :
        # calcule los horarios disponibles y el porcentaje cubierto.
        info = __free_schedule_hours(schedule) 
        percentage = info[0]['total_percentage']

        #calcule el horario y retornelo a la vista. 
        if percentage >= 60:
            return (ubication, __generate_random_schedule(info[1]))

    else:
        return (None, {})




    




