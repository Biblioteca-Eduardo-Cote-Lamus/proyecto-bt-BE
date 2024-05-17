from ubications.models import Ubication
from selection.helpers.student_schedule.student_schedule_helpers import ScheduleStudentManager
from django.db.models.fields.files import FieldFile
from typing import TypedDict, Union
import random 
import numpy as np

class AssignStatistics:

    class InfoDay(TypedDict):
        """
            Clase que tipa la informacion por dia que existe en el horario de la ubicacion.
        """
        dia: str
        todasHorasCubiertas: bool
        horasCubiertas: list[str]
        horasARealizar: list[str]
        porcentajeHorasCubiertas: float

    class AssignStatisticsResponse(TypedDict):
        """
            Clase que tipa la informacion de la asignacion del beca en la ubicacion seleccionada.
        """
        porcentajeDiasCubierto: float
        preseleccionado: bool
        totalDiasFull: int
        diasCubiertos: list[str]
        informacionPorDia: 'AssignStatistics.InfoDay'
        totalHorasACubrir: int
        totalHorasCubiertas: int
        porcentajeHorasCubiertas: float

    @staticmethod
    def get_statistics(*, subschedules, schedule_student, days, is_custom = False):    
        """Funcion que calcula las estadisticas de la asignacion de horarios del beca en la ubicacion seleccionada.

        Args:
            subschedules (list[str]): Lista de los horarios de la ubicacion para el rango de horas.
            schedule_student (list[str]): Lista de los horarios disponibles del beca para cada dia de la semana.
            days (list[str]): Lista de los dias de la semana que tiene asignado el beca.
            is_custom (bool, optional): Indica si el horario seleccionado es personalizado o no. Defaults to False.

        Returns:
            AssignStatisticsResponse: Diccionario con la informacion de la asignacion del beca en la ubicacion seleccionada.
        """
        
        result = []
        total_days_can = 0
        total_hours_can = 0
        total_hours = 0
        for index, scheduleday in enumerate(schedule_student):
            if is_custom:
                subschedule = subschedules[index]
                hours_can =  np.in1d(subschedule,  scheduleday)
            else: 
                subschedule = subschedules
                hours_can =  np.in1d(subschedule,  scheduleday)

            result.append(
                AssignStatistics.InfoDay(
                    dia=days[index],
                    todasHorasCubiertas=np.all(hours_can),
                    horasCubiertas=[ hour for hour, can in zip(subschedule, hours_can) if can ],
                    horasARealizar=subschedule,
                    porcentajeHorasCubiertas=(np.count_nonzero(hours_can)*100)/len(subschedule)
                )
            )
            total_days_can += np.count_nonzero(result[-1]['todasHorasCubiertas'])
            total_hours_can += np.count_nonzero(hours_can)
            total_hours += len(subschedule)
            
        return  AssignStatistics.AssignStatisticsResponse(
            porcentajeDiasCubierto=(total_days_can*100)/len(days),
            preseleccionado=np.all([res['todasHorasCubiertas'] for res in result]),
            totalDiasFull=total_days_can,
            diasCubiertos=[day['dia'] for day in result if day['todasHorasCubiertas']],
            informacionPorDia=result,
            totalHorasACubrir=total_hours,
            totalHorasCubiertas=total_hours_can,
            porcentajeHorasCubiertas=(total_hours_can*100)/total_hours,
        )
        

class AssignUbication:

    # constructor
    def __init__(self):
        self._schedule_types = {
            "unifiedWithoutSaturday": 'unifiedWithoutSaturday',
            "unifiedIncludingSaturday": 'unifiedIncludingSaturday',
            "custom": 'custom',
        }

    
    def assign_random_ubication(self,schedule: Union[ str | FieldFile ]):
        """
            Funcion que asigna una ubicacion de manera aleatoria a un beca.

        Args:
            schedule (Union[ str  |  FieldFile ]): Horario del beca. Puede ser un string o un archivo. Si es string, es la ruta de acceso al archivo.

        Returns:
            tuple( AssignStatistics, Ubication ): Una tupla con la informacion de estadisticas de la asignacion y la ubicacion asignada.
            tuple ( None, None ): En caso de que no se pueda asignar una ubicacion al beca. (El beca no se adapta a ningun horario de la ubicacion)
        """

        # Determine las horas de disponibilidad del beca para cada dia de la semana entre las 6AM y 8PM 
        free_hours = ScheduleStudentManager.get_free_hours(schedule=schedule)['free_schedule_by_day']

        # gurdamos las ubicaciones ya comprobadas
        checked_ubication = set()

        # obtenemos todas las ubicaciones
        allubications = Ubication.objects.all()

        ubication = self.select_random_ubication(checked_ubications=checked_ubication, all_ubications=allubications)

        # Mientras existan ubicaciones por comprobar
        while ubication is not None:

            checked_ubication.add(ubication.id)
            
            beca_schedule_info = self.assign_schedule(
                schedule_ubication=ubication.schedule_format.schedule,
                student_schedule=free_hours,
                is_custom= self.is_custom_schedule(ubication.schedule_type.name)
            )

            # comprobamos si el beca puede ser asignado a la ubicacion
            if beca_schedule_info['porcentajeDiasCubierto'] >= 60 or beca_schedule_info['preseleccionado'] or beca_schedule_info['porcentajeHorasCubiertas'] >= 60:
                return beca_schedule_info, ubication
            
            ubication = self.select_random_ubication(checked_ubications=checked_ubication, all_ubications=allubications)
            
        return None, None
    
    def assign_schedule(self,*, schedule_ubication, student_schedule, is_custom=False):
        """Funcion que determina el algoritmo de seleccion a usar dependiendo del tipo de horario de la ubicacion.

        Args:
            schedule_ubication (list<dict>): Lista de diccionarios que contiene la informacion de los horarios de la ubicacion. Se optiene del modelo ScheduleFormat  en la propiedad "schedule".
            student_schedule (dict[str, list]): Diccionario con keys los dias de la semana hasta el sabado (todo en minisculas y sin tilder), como valor una lista con las horas de disponibilidad del beca.
            is_custom (bool, optional): Valor que indica si el horario es personalizado o no. Por defecto es False.

        Returns:
            dict[list, any]: _description_
        """
        if is_custom:
            return self.assign_custom_ubication(schedule=schedule_ubication, student_schedule=student_schedule)
        else:
            return self.assign_in_unified_schedule(schedule_ubication=schedule_ubication, student_schedule=student_schedule)
            
    def assign_in_unified_schedule(self, *, schedule_ubication, student_schedule):
        """
        Funcion que asigna un horario de manera aleatoria a un beca en una ubicacion con horario unificado.

        Args:
            schedule_ubication (dict[str, list]): Horario de la ubicacion. Se obtiene del ubication.schedule_format.
            student_schedule (list[str]): Lista de las horas disponibles del beca. cada posicion de la lista corresponde a un dia de la semana.

        Returns:
            AssignStatistics: Diccionario con la informacion de la asignacion del beca en la ubicacion seleccionada.
            dict en caso de que no se pueda asignar un horario al beca.
        """
        selected_schedule = set()
        schedule_data = schedule_ubication['schedule']
        schedule_index = self.select_random_schedule(checked_schedules=selected_schedule, all_schedules=schedule_data)

        while schedule_index is not None:
            # seleccionamos un horario de manera aleatoria, en este caso manejamos el indice para no seleccionar el mismo horario
            selected_schedule.add(schedule_index)
            
            # set para controlar los horarios en la propiedad "hours" del horario
            selected_hours = set()
            # seleccionamos el horario que corresponde al indice seleccionado
            selected_schedule_obj = schedule_ubication['schedule'][schedule_index]

            index_hour = self.select_random_schedule(checked_schedules=selected_hours, all_schedules=selected_schedule_obj['hours'])

            while index_hour is not None:

                selected_hours.add(index_hour)

                # seleccionamos la hora que corresponde al indice seleccionado
                hora = selected_schedule_obj['hours'][index_hour]

                # extraemos la hora de inicio y fin del horario
                start, end = hora['start'], hora['end']

                if  'sabado' not in selected_schedule_obj['days'] and len(selected_schedule_obj['days']) == 5: 
                    schedule_student = list(student_schedule.values())[0:-1]
                elif 'sabado' in selected_schedule_obj['days'] and len(selected_schedule_obj['days']) == 6:
                    schedule_student = list(student_schedule.values())
                else:
                    schedule_student = [list(student_schedule.values())[-1]]

                schedule_student_data = AssignStatistics.get_statistics(subschedules=schedule_ubication['scheduleFormat2'][schedule_index][index_hour],
                                                                        schedule_student=schedule_student,
                                                                        days=selected_schedule_obj['days'])


                if (schedule_student_data['porcentajeDiasCubierto']  >= 60) or (schedule_student_data['preseleccionado']) or (schedule_student_data['porcentajeHorasCubiertas'] >= 60):
                    schedule_student_data['schedule_info'] = {"start": start, "end": end} 
                    return schedule_student_data
                
                # en caso de que no se cumpla lo anterior, seleccionamos un nuevo horario, pero eliminamos primero el horario seleccionado
                del selected_schedule_obj['hours'][index_hour]

                index_hour = self.select_random_schedule(checked_schedules=selected_hours, all_schedules=selected_schedule_obj['hours'])
            
            # eliminamos el elemento seleccionado para que no tenga probabilidad de ser seleccionado de nuevo
            del schedule_data[schedule_index]

            # seleccionamos un nuevo horario
            schedule_index = self.select_random_schedule(checked_schedules=selected_schedule, all_schedules=schedule_data)

       
        return {
            'days_percentage': 0,
            'preslected': False,
            'total_days_can': 0,
            'days_cumpliment': []
        }

    def assign_custom_ubication(self,*, schedule, student_schedule):
        """
        Funcion que asigna un horario de manera aleatoria a un beca en una ubicacion con horario personalizado.

        Args:
            schedule (dict[str, list]): Horario de la ubicacion. Se obtiene del ubication.schedule_format.
            student_schedule (list[str]): Lista de las horas disponibles del beca. cada posicion de la lista corresponde a un dia de la semana.
        """

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
        schedulebybeca = self.get_schedule_by_beca(schedule=schedule['schedule'])
        selected_becas = set()
        becas_keys = list(schedulebybeca.keys())

        selected_beca_index = self.select_random_schedule(checked_schedules=selected_becas, all_schedules=becas_keys)

        while selected_beca_index is not None:

            selected_becas.add(selected_beca_index)

            # Seleccionamos alguna key (beca) de manera aleatoria
            random_beca = becas_keys[selected_beca_index]

            # del horario de estudiante, extraemos solo los dias que tiene asignado el beca
            indexes_days = [get_index_day(day[0]) for day in schedulebybeca[random_beca]['days']] 
            subschedulestudent = [ list(student_schedule.values())[index] for index in indexes_days ]

            #  calculamos las estadisticas del beca
            subschedules = [ 
                schedule['scheduleFormat2'][scheduleday[1]][scheduleday[2]] for scheduleday in schedulebybeca[random_beca]['days']
            ]

            schedule_student_data = AssignStatistics.get_statistics(subschedules=subschedules,
                                                                    schedule_student=subschedulestudent,
                                                                    days=[day[0] for day in schedulebybeca[random_beca]['days']],
                                                                    is_custom=True)
            
            if schedule_student_data['porcentajeDiasCubierto']  >= 60 or schedule_student_data['preseleccionado'] or schedule_student_data['porcentajeHorasCubiertas'] >= 60:
                schedule_student_data['schedule_info'] = schedulebybeca[random_beca]['hours']
                schedule_student_data['beca'] = random_beca
                return schedule_student_data
            
            selected_beca_index = self.select_random_schedule(checked_schedules=selected_becas, all_schedules=becas_keys)

                
        return {}
    
    def select_random_ubication(self, *, checked_ubications, all_ubications) -> Ubication | None:
        """Funcion que selecciona una ubicacion de manera aleatoria.

        Args:
            checked_ubications (set): Conjunto de ubicaciones ya comprobadas.
            all_ubications (list[Ubication]): Lista de todas las ubicaciones registradas en el sistemas.

        Returns:
            ubication (Ubication): Ubicacion seleccionada de manera aleatoria.
            None: En caso de que no existan ubicaciones por comprobar.
        """
        while len(checked_ubications) != len(all_ubications):
            location = random.choice(all_ubications)
            if location.id not in checked_ubications:
                return location
        return None

    def select_random_schedule(self, *, checked_schedules, all_schedules) -> int | None :
        """Funcion que selecciona un horario de manera aleatoria.

        Args:
            checked_schedules (set): Conjunto de las horas del horario ya seleccionadas.
            all_schedules (list): Lista de todas las horas del horario.

        Returns:
            int: Indice de la hora seleccionada de manera aleatoria.
            None: En caso de que no existan horas por comprobar.
        """
        while len(checked_schedules) != len(all_schedules):
            schedule_index = random.randint(0, len(all_schedules) - 1)
            if schedule_index not in checked_schedules:
                return schedule_index
        return None

    def is_custom_schedule(self, schedule_type: str):
        """Funcion que determina si el horario es personalizado o no.

        Args:
            schedule_type (str): Tipo de horario de la ubicacion.

        Returns:
            bool: True si el horario es personalizado, False en caso contrario.
        """
        return schedule_type == self._schedule_types['custom']
    
    def get_schedule_by_beca(self, *, schedule):
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




