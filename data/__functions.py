def time_group_check(group):
    if not isinstance(group, list):
        return False
    for time in group:
        if not isinstance(time, str):
            return False
        if not time_check(time):
            return False
    return True


def time_check(time):
    try:
        times = time.split('-')
    except ValueError:
        return False
    if len(times) != 2:
        return False
    for time in times:
        try:
            h, m = time.split(':')
        except ValueError:
            return False
        if len(h) != 2 or len(m) != 2:
            return False
        try:
            h, m = int(h), int(m)
        except ValueError:
            return False
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return False
    if get_minutes(times[0]) >= get_minutes(times[1]):
        return False
    return True


def get_minutes(time):
    h, m = map(int, time.split(':'))
    return h * 60 + m


def time_group_interact(group1, group2):
    for interval1 in group1:
        time1, time2 = interval1.split('-')
        time1, time2 = get_minutes(time1), get_minutes(time2)
        for interval2 in group2:
            time3, time4 = interval2.split('-')
            time3, time4 = get_minutes(time3), get_minutes(time4)
            if time1 <= time3 <= time2 or time1 <= time4 <= time2 or \
                    time3 <= time1 <= time4 or time3 <= time2 <= time4:
                return True
        return False


if __name__ == '__main__':
    print(time_group_interact(['11:00-12:00'], ['09:00-14:00']))
