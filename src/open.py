from datetime import datetime, time


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def isRun(start_hour, end_hour):
    return is_time_between(time(start_hour, 0), time(end_hour, 0))
