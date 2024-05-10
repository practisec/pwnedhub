from datetime import datetime, timezone

def get_current_utc_time():
    return datetime.now(timezone.utc)

def get_local_from_utc(dtg):
    return dtg.replace(tzinfo=timezone.utc).astimezone(tz=None)
