import time
import datetime

def is_Friday():
    return datetime.date.today().weekday() == 4

def find_Friday():
    today = datetime.date.today()
    friday = today + datetime.timedelta( (4-today.weekday()) % 7 )
    return friday

def wait_to_Friday(friday):
    start = datetime.datetime.combine(friday, datetime.time())
    mk_start = time.mktime(start.timetuple())
    mk_now = time.mktime(datetime.datetime.today().timetuple())
    return mk_start - mk_now