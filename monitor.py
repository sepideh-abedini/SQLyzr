import argparse

import psutil
import time

class ProcessUsage:
    proc: psutil.Process
    def __init__(self, pid: int):
        process = psutil.Process(pid)

    @property
    def mem(self):
        total_memory = self.proc.memory_info().rss
        for child in self.proc.children(recursive=True):
            total_memory += child.memory_info().rss
        return total_memory

    @property
    def cpu_(self):
        total_memory = self.proc.memory_info().rss
        for child in self.proc.children(recursive=True):
            total_memory += child.memory_info().rss
        return total_memory




def main(pid):
    process = psutil.Process(pid)
    with open("memory.log", "a") as log_file:
        while True:

            total_cpu = process.cpu_percent(interval=0.1)
            for child in process.children(recursive=True):
                total_cpu += child.cpu_percent(interval=0.1)
            total_memory = total_memory / (1024 * 1024)  # MB
            log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Memory Usage: {total_memory:.2f} MB\n"
            print(log_entry)
            log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Total CPU Usage: {total_cpu:.2f}%\n"
            print(log_entry)
            time.sleep(5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", type=int, required=True)
    args = parser.parse_args()
    main(args.pid)
