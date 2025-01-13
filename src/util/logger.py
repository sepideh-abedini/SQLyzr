import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")


def log(msg):
    if LOG_LEVEL == "DEBUG":
        print(msg)
