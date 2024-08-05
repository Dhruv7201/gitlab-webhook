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

def parse_ISC_datetime(isc_date_str):
    # Define ISC time zone (UTC+5:30)
    ISC = tz.gettz('Asia/Kolkata')
    
    # Parse the ISC datetime string to a naive datetime object
    isc_dt = datetime.fromisoformat(isc_date_str[:-6])  # Remove the timezone offset
    # Attach the ISC timezone information
    isc_dt = isc_dt.replace(tzinfo=ISC)
    
    return isc_dt

def calculate_time_difference(isc_date_str):
    # Get current local datetime with timezone info
    local_now = datetime.now(tz.tzlocal())

    # Parse ISC datetime string
    isc_dt = parse_ISC_datetime(isc_date_str)

    # Calculate the difference in seconds
    time_difference = local_now - isc_dt
    return time_difference.total_seconds()


def format_duration(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    td = str(td).split(".")[0]
    return str(td)
