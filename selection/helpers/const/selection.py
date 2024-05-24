class SelectionConst:
    # Selection
    LIBRARY_SCHEDULE = [
        "06:00-07:00",
        "07:00-08:00",
        "08:00-09:00",
        "09:00-10:00",
        "10:00-11:00",
        "11:00-12:00",
        "12:00-13:00",
        "13:00-14:00",
        "14:00-15:00",
        "15:00-16:00",
        "16:00-17:00",
        "17:00-18:00",
        "18:00-19:00",
        "19:00-20:00",
    ]

    STATUS_ASSIGNATION = {
        "preselected": "Preselected",
        "candidate": "Candidate",
    }

    SCHEDULE_TYPES = {
        'custom': 'custom',
        'unifiedWithoutSaturday': 'unifiedWithoutSaturday',
        'unifiedIncludingSaturday': 'unifiedIncludingSaturday'
    }

    @staticmethod
    def get_index_days(day: str) -> int:
        return {
            "lunes": 0,
            "martes": 1,
            "miercoles": 2,
            "jueves": 3,
            "viernes": 4,
            "sabado": 5,
        }[day]