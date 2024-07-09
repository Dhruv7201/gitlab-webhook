from datetime import datetime, timedelta
from dateutil import tz

def convert_to_ISC(date):
    if date == None:
        return date
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(date[:-4], "%Y-%m-%d %H:%M:%S")

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    central = utc.astimezone(to_zone)
    return central
        

def format_duration(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    return str(td)
