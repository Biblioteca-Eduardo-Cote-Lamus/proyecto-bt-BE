import re

def validate_schedule(schedule) -> tuple[bool, str]:
    days_of_week = {"lunes", "martes", "miercoles", "jueves", "viernes", "sabado"}
    time_pattern = re.compile(r"^(0[0-9]|1[0-2]):[0-5][0-9] (AM|PM)$")

    if not isinstance(schedule, list):
        return False, "El horario debe ser una lista."

    for day_entry in schedule:
        if not isinstance(day_entry, dict):
            return False, f"Cada entrada del horario debe ser un diccionario. Entrada no válida: {day_entry}"
        if "day" not in day_entry or "hours" not in day_entry:
            return False, f"Cada entrada debe tener las claves 'day' y 'hours'. Entrada no válida: {day_entry}"
        if day_entry["day"] not in days_of_week:
            return False, f"El día '{day_entry['day']}' no es válido. Debe ser uno de {days_of_week}."
        if not isinstance(day_entry["hours"], list):
            return False, f"Las horas deben ser una lista. Entrada no válida: {day_entry['hours']}"

        for hour_entry in day_entry["hours"]:
            if not isinstance(hour_entry, dict):
                return False, f"Cada entrada de horas debe ser un diccionario. Entrada no válida: {hour_entry}"
            if "start" not in hour_entry or "end" not in hour_entry:
                return False, f"Cada entrada de horas debe tener las claves 'start' y 'end'. Entrada no válida: {hour_entry}"
            if not time_pattern.match(hour_entry["start"]) or not time_pattern.match(hour_entry["end"]):
                return False, f"El formato de las horas debe ser HH:MM AM/PM. Entrada no válida: {hour_entry}"
            if "valid" in hour_entry and not isinstance(hour_entry["valid"], bool):
                return False, f"El campo 'valid' debe ser un booleano si está presente. Entrada no válida: {hour_entry}"

    return True, "El horario es válido."