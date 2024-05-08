
def verify_schedule(schedule) -> bool:
    return __verify_keys(schedule)

def __verify_keys(schedule):
    """Verica que las keys del json sean las correctas

    Args:
        schedule (dict): Diccionario con la informacion del horario de la ubicaicon

    Returns:
        bool: True si las keys son correctas, False en caso contrario
    """

    # extraemos las keys del diccionario
    keys = schedule.keys()
   
    # solo deben de haber dos keys
    if len(keys) != 2:
        return False
    
    # verificamos que el nombre de las keys sean las correctas: scheduleType y schedule deben de estar
    if 'scheduleType' not in keys or 'schedule' not in keys:
        return False
    
    # verficamos que el valor de las keys sean string 
    if type(schedule['scheduleType']) != str or type(schedule['schedule']) != list:
        return False
    
    # verficamos que el valor de las keys sean correctos 
    if schedule['scheduleType'] not in ['unifiedWithoutSaturday', 'unifiedIncludingSaturday', 'custom']:
        return False
    
    # verificamos que el valor de schedule sea un array de dict
    if type(schedule['schedule']) != list:
        return False
    
    # verificamos que el array no este vacio
    if len(schedule['schedule']) == 0:
        return False
    
    # verificamos que todos los elementos del array tenga la estructura correcta
    if schedule['scheduleType'] in  ['unifiedWithoutSaturday', 'unifiedIncludingSaturday', 'custom']:
        # verificamos que el array tenga la estructura correcta
        for day in schedule['schedule']:
            day_keys = day.keys()
            
            if type(day) != dict:
                return False
            
            if 'days' not in day_keys or 'hours' not in day_keys:
                return False
            
            if type(day['days']) != list or type(day['hours']) != list:
                return False
            
            # verificar que los dias sean correctos
            if not __verify_available_days(day['days']):
                return False
            
            # verificar que las horas tenga la estructura correct
            if not __verify_hours_structure(day['hours']):
                return False
        
    else:
        return False

    return True


def __verify_available_days(days):
    """Verifica que los dias enviados sean correctos

    Args:
        days (list): Lista con los dias del horario

    Returns:
        bool: True si los dias son correctos, False en caso contrario
    """
    for day in days:
        if day not in ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado']:
            return False
    return True

def __verify_hours_structure(hours):
    """Verifica que la estructura de las horas sea correcta

    Args:
        hours (list): Lista con las horas del horario

    Returns:
        bool: True si la estructura es correcta, False en caso contrario
    """
    permited_hours = [
        '06:00 AM',
        '07:00 AM',
        '08:00 AM',
        '09:00 AM',
        '10:00 AM',
        '11:00 AM',
        '12:00 PM',
        '01:00 PM',
        '02:00 PM',
        '03:00 PM',
        '04:00 PM',
        '05:00 PM',
        '06:00 PM',
        '07:00 PM',
        '08:00 PM',
    ]

    for hour in hours:

        if type(hour) != dict:
            return False
        
        hour_keys = hour.keys()

        if  ('start' not in hour_keys) or \
            ('end' not in hour_keys) or \
            ('valid' not in hour_keys) or \
            ('becas' not in hour_keys):
            return False
        
        if (type(hour['start']) != str) or \
            (type(hour['end']) != str) or \
            (type(hour['valid']) != bool) or \
            (type(hour['becas']) != int) and (type(hour['becas']) != list):
            return False
        
        if hour['start'] not in permited_hours or hour['end'] not in permited_hours:
            return False
        
    return True
    