import datetime

LOG_LEVEL = 'DEBUG'


class Timer():
    def __init__(self):
        pass

    def start(self):
        self.start_time = datetime.datetime.now()

    def stop(self):
        return datetime.datetime.now() - self.start_time


def log(*args):
    if LOG_LEVEL == 'DEBUG':
        print(*args)