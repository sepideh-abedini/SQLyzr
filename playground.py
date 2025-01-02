import asyncio
import os
from datetime import datetime, timezone, timedelta
import random
from asyncio import Lock
from typing import List

from openai import AsyncClient
from openai.types.chat import ChatCompletion

from src.cat.catter import Catter
from src.eval.lib import Timer
from src.gpt.models import BatchInputRequest
from src.parse.graph_drawer import draw_graph
from src.parse.parser import SqlParser


# catter = Catter()
#
# sql = "SELECT T1.`School Name`, T2.Street, T2.City, T2.State, T2.Zip FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Monterey' AND T1.`Free Meal Count (Ages 5-17)` > 800 AND T1.`School Type` = 'High Schools (Public)'"
# sql = "SELECT T2.School, T1.AvgScrWrite, T2.Phone FROM schools AS T2 LEFT JOIN satscores AS T1 ON T2.CDSCode = T1.cds WHERE strftime('%Y', T2.OpenDate) > '1991' OR strftime('%Y', T2.ClosedDate) < '2000'"
# sql = "SELECT x FROM schools WHERE strftime('%Y', T2.OpenDate) > '1991'"
# parser = SqlParser()
# draw_graph(parser.parse(sql), "graph.png")
#
# cat = catter.get_category(sql)
# print(cat)

class GptGatewayException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class GptRateLimits:
    tokens_per_min: int = 200_000
    batch_queue: int = 2_000_000
    req_per_min: int = 500


class GptUsage:
    tokens: int
    expires_at: datetime

    def __init__(self, tokens: int):
        self.tokens = tokens
        self.expires_at = datetime.utcnow() + timedelta(seconds=60)

    def expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    def expire(self):
        self.expires_at = datetime.utcnow()


class GptUsageTracker:
    __instance: 'GptUsageTracker' = None
    limits: GptRateLimits

    __usage: List[GptUsage]
    total_tokens: int
    lock: Lock

    def __init__(self):
        self.__usage = []
        self.total_tokens = 0
        self.lock = asyncio.Lock()
        self.limits = GptRateLimits()

    async def check_limit(self, tokens: int):
        await self.lock.acquire()
        try:
            self.__update_total_tokens()
            print(f"Checking Limit: {tokens}+{self.total_tokens}/{self.limits.tokens_per_min}")
            if tokens + self.total_tokens > self.limits.tokens_per_min:
                return False
            return True
        finally:
            self.lock.release()

    async def add_usage(self, tokens: int):
        await self.lock.acquire()
        try:
            usage = GptUsage(tokens)
            old_total = self.total_tokens
            self.__usage.append(usage)
            self.total_tokens += usage.tokens
            print(f"Usage added: {old_total} => {self.total_tokens}")
            return usage
        finally:
            self.lock.release()

    def __update_total_tokens(self):
        while len(self.__usage) > 0:
            usage = self.__usage[0]
            if not usage.expired():
                break
            old_tokens = self.total_tokens
            self.total_tokens -= usage.tokens
            self.__usage.pop(0)
            print(f"Expired token: {usage.tokens}, {old_tokens} => {self.total_tokens}")

    @staticmethod
    def get_instance():
        if not GptUsageTracker.__instance:
            GptUsageTracker.__instance = GptUsageTracker()
        return GptUsageTracker.__instance


class GptGateway:
    client: AsyncClient
    tracker: GptUsageTracker

    def __init__(self):
        self.client = AsyncClient(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=5
        )
        self.tracker = GptUsageTracker.get_instance()

    async def __send_without_tracking(self, request: BatchInputRequest):
        print("Sending GPT Request")
        result = await self.client.chat.completions.create(
            **request.body.dict()
        )
        print("Received GPT Response")
        return result

    async def track_and_send(self, request: BatchInputRequest):
        tokens = request.get_token_usage()
        can_send = await self.tracker.check_limit(tokens)
        if can_send:
            usage = await self.tracker.add_usage(tokens)
            result = await self.__send_without_tracking(request)
            usage.expire()
            return result
        else:
            raise GptGatewayException("Token limit hit!")


async def bar(i):
    gw = GptUsageTracker.get_instance()
    await asyncio.sleep(random.randint(1, 20))
    tokens = await gw.__update_total_tokens()
    print(f"[{i}]: Before {tokens}")
    new_toks = random.randint(100, 200)
    print(f"[{i}]: Adding {new_toks}")
    await gw.add_usage(new_toks)
    tokens = await gw.__update_total_tokens()
    print(f"[{i}]: After {tokens}")
    await asyncio.sleep(random.randint(1, 4))


async def main():
    timer = Timer()
    timer.start()
    gw = GptGateway()
    reqs = []
    with open("data/din/pred_0.0_0.txt.classif.in.jsonl") as file:
        for line in file.readlines():
            req = BatchInputRequest.model_validate_json(line)
            reqs.append(req)

    futures = []
    for req in reqs:
        future = gw.track_and_send(req)
        futures.append(future)
        print(f"{req.custom_id} sent")
        # print(res)
        # futures.append(gw.track_and_send(req))

    ress = await asyncio.gather(*futures)
    print(ress)
    print(timer.stop())


if __name__ == '__main__':
    asyncio.run(main())
