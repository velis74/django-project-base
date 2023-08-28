import datetime


def utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


def now_ts():
    return int(datetime.datetime.now().timestamp())
