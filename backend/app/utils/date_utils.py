from datetime import datetime, timedelta
from dateutil import tz


def convert_to_ISC(
    date,
):  # This function is used to convert the date to the ISC timezone
    if date is None:
        return date

    # Timezones
    from_zone = tz.tzutc()  # UTC timezone
    to_zone = (
        tz.tzlocal()
    )  # Local timezone (should automatically detect your local timezone)

    # Parse the date string based on its format
    if len(date) == 10:
        # Handle date-only format
        utc = datetime.strptime(date, "%Y-%m-%d")
    elif "+" in date:
        # Extract the date portion if it's in UTC and has a timezone offset
        utc = datetime.strptime(date.split(" ")[0], "%Y-%m-%d")
    else:
        # Handle date in UTC or just in plain format
        if "UTC" in date:
            utc = datetime.strptime(date[:-4], "%Y-%m-%d %H:%M:%S")
        else:
            utc = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    # Localize the datetime to UTC
    utc = utc.replace(tzinfo=from_zone)  # Make it timezone-aware

    # Convert to local time zone
    local_time = utc.astimezone(to_zone)
    return local_time


def parse_ISC_datetime(
    isc_date_str,
):  # this function is used to parse the date in the ISC timezone
    # Define ISC time zone (UTC+5:30)
    ISC = tz.gettz("Asia/Kolkata")

    # Parse the ISC datetime string to a naive datetime object
    isc_dt = datetime.fromisoformat(isc_date_str[:-6])  # Remove the timezone offset
    # Attach the ISC timezone information
    isc_dt = isc_dt.replace(tzinfo=ISC)

    return isc_dt


def calculate_time_difference(
    isc_date_str,
):  # this function is used to calculate the time difference between the current time and the ISC time
    # Get current local datetime with timezone info
    local_now = datetime.now(tz.tzlocal())

    # Parse ISC datetime string
    isc_dt = parse_ISC_datetime(isc_date_str)

    # Calculate the difference in seconds
    time_difference = local_now - isc_dt
    return time_difference.total_seconds()


def format_duration(
    seconds: float,
) -> str:  # this function is used to format the duration in the string format
    td = timedelta(seconds=seconds)
    td = str(td).split(".")[0]
    return str(td)


def convert_to_IST(
    utc_dt,
):  # this function is used to convert the date to the IST timezone
    # Define UTC time zone
    UTC = tz.gettz("UTC")
    # Define IST time zone (UTC+5:30)
    IST = tz.gettz("Asia/Kolkata")
    if utc_dt[-1] == "Z":
        utc_dt = datetime.fromisoformat(utc_dt[:-1])
    else:
        utc_dt = datetime.fromisoformat(utc_dt.replace("Z", "+00:00"))
    # Attach the UTC timezone information
    utc_dt = utc_dt.replace(tzinfo=UTC)

    # Convert time zone
    ist_dt = utc_dt.astimezone(IST)
    return ist_dt


def formate_date_range(
    date_range,
):  # this function is used to format the date range to the IST timezone by converting the UTC to IST with the help of the convert_to_IST function
    if date_range.get("from") and date_range.get("to"):
        # Convert UTC to IST for both "from" and "to" dates
        date_range["from"] = convert_to_IST(date_range["from"])
        date_range["to"] = convert_to_IST(date_range["to"])

        if date_range["from"] == date_range["to"]:
            # If "from" and "to" are the same, set "from" to the start of the day and "to" to the end of the day
            date_range["from"] = date_range["from"].replace(hour=0, minute=0, second=0)
            date_range["to"] = date_range["to"].replace(hour=23, minute=59, second=59)
        else:
            # Ensure "from" starts at 00:00:00 and "to" ends at 23:59:59
            date_range["from"] = date_range["from"].replace(hour=0, minute=0, second=0)
            date_range["to"] = date_range["to"].replace(hour=23, minute=59, second=59)
    elif date_range.get("from") and not date_range.get("to"):
        date_range["from"] = convert_to_IST(date_range["from"])
        date_range["from"] = date_range["from"].replace(hour=0, minute=0, second=0)
        date_range["to"] = date_range["from"]
        date_range["to"] = date_range["to"].replace(hour=23, minute=59, second=59)

    else:
        # from = one month ago, to = today
        date_range["to"] = datetime.now()
        date_range["from"] = date_range["to"] - timedelta(days=30)
    return date_range
