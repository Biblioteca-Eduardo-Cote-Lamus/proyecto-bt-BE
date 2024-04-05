from datetime import datetime


def left_time(first_date, second_date):
    """
        This function calculates the time left between two dates
        :param first_date: datetime object
        :param second_date: datetime object
        :return: dictionary with the days, hours, minutes and seconds left between the two dates
    """
    timeleft = datetime.fromisoformat(first_date) - datetime.fromisoformat(second_date)
    return  {
        "days": timeleft.days,
        "hours": timeleft.seconds // 3600,
        "minutes": (timeleft.seconds // 60) % 60,
        "seconds": timeleft.seconds % 60,
    }