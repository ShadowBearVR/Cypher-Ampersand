import time
from datetime import datetime
import json

def format_server_time():
    server_time = time.localtime()
    return time.strftime("%I:%M:%S %p", server_time)

env_vars = {}
def set_env_vars():
    global env_vars
    with open('env/.env', 'r') as env_file:
        env_vars = json.load(env_file)

def get_env_var(key):
    return env_vars[key]
        
