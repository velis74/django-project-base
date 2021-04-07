import datetime


def utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
