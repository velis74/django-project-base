import datetime


def _utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)