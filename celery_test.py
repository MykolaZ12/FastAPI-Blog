from celery import Celery

from config import celeryconfig

celery2 = Celery('celery_test', broker=celeryconfig.broker_url, backend=celeryconfig.result_backend)


@celery2.task
def add(x, y):
    return x + y


if __name__ == '__main__':
    import time
    task = add.delay(1, 2)
    while not task.ready():
        print(task.state)
        time.sleep(1)
    print(task.get())