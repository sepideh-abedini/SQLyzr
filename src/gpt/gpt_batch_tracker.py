import asyncio
import json
import os.path
from asyncio import Lock
from dataclasses import dataclass
from typing import Dict, Optional

from pydantic import BaseModel

from src.gpt.gpt_gateway import GptRateLimitException
from src.gpt.gpt_limits import GptRateLimits
from src.gpt.models import BatchInputRequest


def get_req_file_token_usage(in_path: str):
    in_file = open(in_path)
    total_tokens = 0
    for line in in_file.readlines():
        req = BatchInputRequest.model_validate_json(line)
        total_tokens += req.get_token_usage()
    return total_tokens


class BatchJobState(BaseModel):
    in_path: str
    tokens: int
    batch_id: Optional[str] = None
    file_id: Optional[str] = None
    out_file_id: Optional[str] = None

    def in_flight(self):
        return self.batch_id is not None and self.out_file_id is None


class GptBatchState(BaseModel):
    states: Dict[str, BatchJobState] = dict()

    def total_tokens(self):
        in_flight_states = filter(lambda s: s.in_flight(), self.states.values())
        return sum(map(lambda s: s.tokens, in_flight_states))


class GptBatchTracker:
    __instance: 'GptBatchTracker' = None
    save_path: str = ".batch.state.json"
    limits: GptRateLimits
    state: GptBatchState

    lock: Lock

    def __init__(self):
        self.__usage = []
        self.lock = asyncio.Lock()
        self.limits = GptRateLimits()
        try:
            with open(self.save_path) as file:
                data = json.load(file)
                self.state = GptBatchState.model_validate(data)
        except Exception:
            self.state = GptBatchState.model_validate(dict())

    def total_tokens(self):
        return self.state.total_tokens()

    def save(self):
        with open(self.save_path, "w") as file:
            file.write(json.dumps(self.state.dict(), indent=4))

    async def get_state(self, in_path: str) -> BatchJobState:
        await self.lock.acquire()
        try:
            if in_path not in self.state.states:
                self.state.states[in_path] = BatchJobState.model_validate(
                    {"in_path": in_path, "tokens": get_req_file_token_usage(in_path)})
            return self.state.states[in_path]
        finally:
            self.lock.release()

    async def set_state(self, state: BatchJobState):
        await self.lock.acquire()
        try:
            self.state.states[state.in_path] = state
        finally:
            self.lock.release()
            self.save()

    # async def on_batch_create(self, idx: str, tokens: int):
    #     await self.lock.acquire()
    #     try:
    #         print(f"Checking Token Limit: {tokens}+{self.total_tokens()}/{self.limits.batch_queue}")
    #         if tokens + self.total_tokens() > self.limits.batch_queue:
    #             raise GptRateLimitException()
    #         old_total = self.total_tokens()
    #         self.batches[idx] = tokens
    #         print(f"Token usage added: {old_total} => {self.total_tokens()}")
    #         self.save()
    #         return True
    #     finally:
    #         print(self.batches)
    #         self.lock.release()

    @staticmethod
    def get_instance():
        if not GptBatchTracker.__instance:
            GptBatchTracker.__instance = GptBatchTracker()
        return GptBatchTracker.__instance
