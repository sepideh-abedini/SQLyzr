import re
from typing import Dict, Optional, List

from pydantic import BaseModel

from src.configs.config_loader import load_config
from src.util.model_utils import read_jsonl


class LogTimeInfo(BaseModel):
    timestamp: float


class LogRecord(BaseModel):
    extra: Optional[Dict] = None
    time: LogTimeInfo


class LogEntry(BaseModel):
    record: LogRecord

    @property
    def idx(self):
        return self.record.extra['idx']

    @property
    def timestamp(self):
        return self.record.time.timestamp

    @property
    def is_start(self):
        return 'start' in self.record.extra

    @property
    def is_finish(self):
        return 'finish' in self.record.extra


def get_time(idx: str, entries: List[LogEntry]):
    result = 0
    start = 0
    finish = 0
    conf = load_config("dail.bird.small.json")
    td = dict()
    for run_conf in conf.eval_conf.get_run_confs():
        tmp, itr = run_conf.temp, run_conf.itr
        td[(tmp, itr)] = []
        for e in entries:
            match = re.search(f".*{tmp}_{itr}.*", e.idx)
            if match:
                td[(tmp, itr)].append(e)

    for (tmp, itr), entries in td.items():
        print(tmp, itr)
        print(len(entries))

    # filtered = list(filter(lambda e: e.idx == idx, entries))
    # for e in filtered:
    #     if e.is_start:
    #         start = e.timestamp
    #     if e.is_finish:
    #         finish = e.timestamp
    # print(f"{idx}: {finish - start}")


def parse_dail_timing(log_path):
    data = read_jsonl(log_path, LogEntry)
    get_time("DAIL:DailSchemaLinksGenerator", data)
    get_time("DAIL:DailQuestionGenerator", data)


def main():
    parse_dail_timing("timing.jsonl")


if __name__ == '__main__':
    main()
