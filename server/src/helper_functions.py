import time
from datetime import datetime

def format_server_time():
    server_time = time.localtime()
    return time.strftime("%I:%M:%S %p", server_time)