#Declaro las constantes a usar:

#dias de la semaa
__diasSemana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado']

#horarios permitidos
__horarios_permitidos = [
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
    '20:00-21:00',
    '21:00-22:00',
]


def schedule_formart(schedule):
    """
        Genera un diccionario para ser guardado como json de la estructura final del horario

        Args:
            schedule (dict): Diccionario con la informacion del tipo de horario y la los horarios por dia
                            { scheduleFormat: list<list<str>>, scheduleFormat2: list<list<List<str>>> }
    """

    def gen_schedule_format_flat(schedule):
        """
            Esta funcion se encarga de aplanar los rangos de hora por cada dia en un solo arreglo. 
        Args:
            schedule (list): Una lista de lista de lista [[[]]] de string con los horarios de cada dia

        Returns:
           list: Retorna una lista de lista de string con los horarios de cada dia [  [], [], ..., [] ]
        """
        aplanado = []

        for dia in schedule:
            aplanado.append([])
            for subdia in dia:
                aplanado[-1].extend(subdia)
        return aplanado

    schedules = list( map(__schedule_obj, schedule['schedule']) )
    return  {
        "scheduleFormat": gen_schedule_format_flat(schedules),
        "scheduleFormat2": schedules
    }

def __schedule_obj(schedule):
    """
        Genera un diccionario ( o JSON) con la informacion del horario a guardar: days, hours

    Args:
        schedule (dict): Diccionario con la informacion del horario de la ubicaicon

    Returns:
       list (str): Una lista con todas las horas que se forman en cada dia disponible
    """

    #Aclaracion importante: el map de __generate_hours_between genera un lista de lista, por lo cual es necesario aplanarla (flat) para generar un solo rango de horas para ese dia
    #ejemplo, [ ['06:00-07:00', '07:00-08:0'], ['10:00-11:00'] ] deberiamos obtener [ '06:00-07:00', '07:00-08:0', '10:00-11:00' ]
    # para lograr ese se hace uso de un lista comprimida

    # return [
    #     hour for rangeHoursList in list(map(__generate_hours_between, schedule['hours'])) \
    #     for hour in rangeHoursList
    # ]
    return list(map(__generate_hours_between, schedule['hours']))

def __generate_hours_between(hours):
    """
       Genera las horas que existen entre la hora de inicio y fin en formato xx:xx-yy:yy

    Args:
        hours (dict): Un diccionario cuya estructura es: {"start": str, "end": str, "valid": bool, "becas": number | list }

    Returns:
        list: Se retorna una lista con las horas intermedias en formato str xx:xx-yy:yy
    """

    startValues = hours['start'].split(' ')
    endValues = hours['end'].split(' ')

    # Verificamos que tanto la hora de inicio y fin son pm y a su vez si no son 12 para sumar 12 y obtener un formato en 24horas
    if startValues[1] == 'PM':
        # validamos que no sean las 12
        if not '12' in startValues[0] :
            startValues[0] = f'{int(startValues[0].split(':')[0]) + 12}:00'

    if endValues[1] == 'PM':
        # validamos que no sean las 12
        if not '12' in endValues[0] :
            endValues[0] = f'{int(endValues[0].split(':')[0]) + 12}:00'


    #encontramos los indeces y generamos un slice

    startIndex = next((i for i, time in enumerate(__horarios_permitidos) if time.startswith(startValues[0])), None)

    endIndex = next((i for i, time in enumerate(__horarios_permitidos) if time.startswith(endValues[0])), None)

    return __horarios_permitidos[ startIndex : endIndex ]



