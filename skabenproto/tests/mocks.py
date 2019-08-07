import random
import time

dev_types = [
    'lock',
    'term',
    'dumb',
]

TS = int(time.time())
UID = '00ff00ff00ff'
TASK_ID = '51048'

def get_random_from(_list):
    i = random.randint(0, len(_list)-1)
    return _list[i]