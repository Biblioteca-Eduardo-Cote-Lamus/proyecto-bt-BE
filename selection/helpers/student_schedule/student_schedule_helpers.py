from typing import Dict, List, TypedDict, Union, Literal
from django.db.models.fields.files import FieldFile
from ..const.selection import SelectionConst
import tabula as tb

class FreeHoursResult(TypedDict):
    """
        Clase que representa el resultado de la función get_free_hours
    Args:
        TypedDict (): Clase base de TypedDict
    """
    
    free_hours: Dict[
        Literal[ 'total', 'total_percentage' ], 
        int
    ]

    free_schedule_by_day: Dict [
        Literal['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'] , 
        List[str]
    ]


class ScheduleStudentManager:
    """
        Clase que se encarga de obtener las horas libres de un estudiante
    """

    @staticmethod
    def get_free_hours(schedule: Union[FieldFile, str]) -> FreeHoursResult:
        """Funcion que se encarga de obtener las horas libres de un estudiante a partir de su horario 

        Args:
            schedule (Union[FieldFile, str]): Horario del estudiante. Puede ser la ruta de acceso al archivo o el archivo en si.

        Returns:
            FreeHoursResult: Resultado de la función. Contiene las horas libres y las horas libres por dia.
        """
        # dias de la semana 
        days = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado']
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
                if value == '.' and row[0] in SelectionConst.LIBRARY_SCHEDULE :
                    # por tanto. al diccionario, para ese dia, agregamos la franja horario que siempre se encuentra en la posicion 0 
                    free_schedule_by_day[days[index - 1]].append(row[0])
                    free_hours['total'] += 1

        free_hours['total_percentage'] = (free_hours['total']*100)/(len(SelectionConst.LIBRARY_SCHEDULE)*6)

        return FreeHoursResult(free_hours=free_hours, free_schedule_by_day=free_schedule_by_day)