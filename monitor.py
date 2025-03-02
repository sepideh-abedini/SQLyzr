import argparse
import sys
from typing import TypedDict

import psutil
import time

from loguru import logger


class ProcessUsage:
    proc: psutil.Process

    def __init__(self, pid: int):
        self.proc = psutil.Process(pid)

    @property
    def mem(self):
        total_memory = self.proc.memory_info().rss
        for child in self.proc.children(recursive=True):
            total_memory += child.memory_info().rss
        total_memory = total_memory / (1024 * 1024)  # MB
        return total_memory

    @property
    def cpu(self):
        total_cpu = self.proc.cpu_percent(interval=0.1)
        for child in self.proc.children(recursive=True):
            total_cpu += child.cpu_percent(interval=0.1)
        return total_cpu

    @property
    def cpu_time(self):
        total_cpu = sum(self.proc.cpu_times())
        for child in self.proc.children(recursive=True):
            total_cpu += sum(child.cpu_times())
        return total_cpu

    def __repr__(self):
        return str(self)

    def __str__(self):
        msg = "Usage Info\n"
        msg += f"Memory Usage: {self.mem:.2f} MB\n"
        msg += f"Total CPU Usage: {self.cpu:.2f}%\n"
        msg += f"Total CPU Time: {self.cpu_time}\n"
        return msg

    def to_dict(self):
        return {
            'cpu': self.cpu,
            'mem': self.mem,
            'cpu_time': self.cpu_time
        }


def main(pid):
    try:
        logger.remove(0)
    except Exception:
        pass
    logger.add("util.log", level="INFO")
    logger.add("util.jsonl", level="INFO", serialize=True)
    logger.add(sys.stderr, level="INFO", colorize=True, enqueue=True,
               format="<green>{time:HH:mm:ss} | </green><level> {level}: {message}</level>")
    pu = ProcessUsage(pid)
    while True:
        logger.info(str(pu), util=pu.to_dict())
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", type=int, required=True)
    args = parser.parse_args()
    main(args.pid)
