import uuid
from dateutil import tz


def localize_datetime(fromtime):
    return fromtime.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())


def format_datetime(value, format=None):
    value = localize_datetime(value)
    return value.strftime(format or "%Y-%m-%d %H:%M:%S %z")


def format_isodatetime(value):
    if value.utcoffset() is None:
        value = value.replace(tzinfo=tz.tzutc())

    return value.isoformat()


def format_currency(value):
    return "${:,.2f}".format(value)


def format_uuid(value):
    try:
        return uuid.UUID(value)
    except ValueError:
        return None
