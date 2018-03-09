from celery import Celery
from qingdian_jian.settings import DEBUG

if DEBUG:
    REDIS_HOST = '10.10.6.5'
    REDIS_PORT = 6012
else:
    REDIS_HOST = '10.10.10.3'
    REDIS_PORT = 6000
REDIS_DB = 15
broker = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
app = Celery('tasks', broker=broker, backend=backend)


@app.task
def add(x, y):
    return x + y
