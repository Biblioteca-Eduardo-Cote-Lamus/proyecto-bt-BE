from .schedule_format import schedule_formart


def generate_schedule_format(ubication):

    schedules_by_days = {}
        # agrupamos los horarios por dia
    for schedule in ubication.schedules.values('start_hour', 'end_hour', 'total_becas', 'becas_json', 'days'):
        if schedule['days'] not in schedules_by_days:
            schedules_by_days[schedule['days']] = []
            schedules_by_days[schedule['days']].append(schedule)
        else:
            schedules_by_days[schedule['days']].append(schedule)

    scheduleObj = {
        "scheduleType": ubication.schedule_type.name,
        "schedule": [
            {
                "days": day.split(', '),
                "hours": [
                    {
                        "start": schedule['start_hour'],
                        "end": schedule['end_hour'],
                        "becas": schedule['total_becas'] if schedule['becas_json'] is None else schedule['becas_json']
                    } for schedule in schedules
                ]
            } for day, schedules in schedules_by_days.items()
        ],
    }
    hours_between = schedule_formart(scheduleObj)
    scheduleObj['scheduleFormat'] = hours_between
    return scheduleObj