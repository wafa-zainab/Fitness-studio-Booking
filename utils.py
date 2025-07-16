# utils.py
import pytz
from datetime import datetime
def convert_ist_to_timezone(dt_str: str, target_tz: str) -> str:
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    ist = pytz.timezone("Asia/Kolkata")
    dt_ist = ist.localize(dt)
    target = pytz.timezone(target_tz)
    return dt_ist.astimezone(target).strftime("%Y-%m-%d %H:%M")
