import asyncio
import datetime
import json
import os.path
from asyncio import Lock
from typing import Dict, Optional, List, Callable, Coroutine, Literal

from openai.types import Batch
from pydantic import BaseModel
from datetime import datetime, timedelta

from src.gpt.gpt_client import GptBatchClient
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


BatchStatus = Literal[
    "validating", "failed", "in_progress", "finalizing", "completed", "expired", "cancelling", "cancelled"]


class BatchTracker:
    __instance: 'GptBatchTracker' = None
    batch_client: GptBatchClient
    batch_tokens: Dict[str, int]
    save_path: str = ".batch.tokens.json"
    limits: GptRateLimits
    lock: Lock

    def __init__(self):
        self.batch_client = GptBatchClient()
        self.load()
        self.lock = asyncio.Lock()
        self.limits = GptRateLimits()
        print(f"Current token usage: {self.total_tokens()}/{self.limits.batch_tokens_per_day}")

    def save(self):
        with open(self.save_path, "w") as file:
            file.write(json.dumps(self.batch_tokens, indent=4))

    def load(self):
        if not os.path.exists(self.save_path):
            self.batch_tokens = dict()
            self.save()

        cur_batches = self.batch_client.list_cur_batches()
        cur_bids = set(map(lambda b: b.id, cur_batches))
        with open(self.save_path) as file:
            self.batch_tokens = json.load(file)
        for bid in self.batch_tokens.keys():
            if bid not in cur_bids:
                self.batch_tokens.pop(bid)

    def should_count(self, batch: Batch) -> bool:
        if not batch.in_progress_at and batch.status != "validating":
            return False
        return True

    def total_tokens(self) -> int:
        cur_batches = self.batch_client.list_cur_batches()
        cur_batches = filter(self.should_count, cur_batches)
        tokens = 0
        for batch in cur_batches:
            tokens += self.batch_tokens[batch.id]
        return tokens

    def tokens_exceed_limit(self, tokens: int):
        total_tokens = self.total_tokens()
        new_total = tokens + total_tokens
        print(f"Checking Token Limit: {tokens}+{total_tokens} = {new_total} /{self.limits.batch_tokens_per_day}")
        return new_total > self.limits.batch_tokens_per_day

    async def init_batch(self, in_path):
        await self.lock.acquire()
        tokens = get_req_file_token_usage(in_path)
        if self.tokens_exceed_limit(tokens):
            self.lock.release()
            raise GptRateLimitException()

    def commit_batch(self, in_path: str, bid: str):
        try:
            tokens = get_req_file_token_usage(in_path)
            self.batch_tokens[bid] = tokens
        finally:
            self.lock.release()
            self.save()

    @staticmethod
    def get_instance():
        if not BatchTracker.__instance:
            BatchTracker.__instance = BatchTracker()
        return BatchTracker.__instance

# class BatchJobState(BaseModel):
#     bid: str
#     tokens: int
#     expires_at: datetime
#     status: BatchStatus
#
#     def count_tokens(self):
#         return self.status not in ["failed", "completed", "cancelled", "expired"]
#
#     def expired(self) -> bool:
#         return datetime.utcnow() > self.expires_at
#

# class GlobalBatchJobs(BaseModel):
#     batches: Dict[str, BatchJobState]
#
#     def total_tokens(self):
#         pass
#

# class GptBatchTracker:
#     __instance: 'GptBatchTracker' = None
#     save_path: str = ".batch.state.json"
#     limits: GptRateLimits
#     # global_state: GlobalBatchJobs
#
#     lock: Lock
#
#     def __init__(self):
#         self.__usage = []
#         self.lock = asyncio.Lock()
#         self.limits = GptRateLimits()
#         try:
#             with open(self.save_path) as file:
#                 data = json.load(file)
#                 self.state = GlobalBatchJobs.model_validate(data)
#         except Exception:
#             self.state = GlobalBatchJobs.model_validate(dict())
#
#     def save(self):
#         data = json.dumps(self.global_state.dict(), indent=4)
#         with open(self.save_path, "w") as file:
#             file.write(data)
#
#     async def exclusive_call(self, fn: Callable):
#         await self.lock.acquire()
#         try:
#             fn()
#         finally:
#             self.lock.release()
#             self.save()
#
#     async def update_status(self, bid: str, status: str):
#         await self.lock.acquire()
#         try:
#             self.global_state.batches[bid].status = status
#         finally:
#             self.lock.release()
#             self.save()
#
#     def tokens_exceed_limit(self, tokens: int):
#         total_tokens = self.total_tokens()
#         new_total = tokens + total_tokens
#         print(f"Checking Token Limit: {tokens}+{total_tokens} = {new_total} /{self.limits.batch_queue}")
#         return new_total > self.limits.batch_queue
#
#     async def init_batch(self, in_path: str):
#         await self.lock.acquire()
#         tokens = get_req_file_token_usage(in_path)
#         if self.tokens_exceed_limit(tokens):
#             self.lock.release()
#             raise GptRateLimitException()
#         else:
#             async def commit_hook(bid: str, status: str):
#                 await self.commit_batch(in_path, bid, status)
#
#             # return commit_hook
#
#     async def commit_batch(self, in_path: str, bid: str, status: str):
#         try:
#             tokens = get_req_file_token_usage(in_path)
#             expires_at = datetime.utcnow() + timedelta(days=1)
#             state = BatchJobState.model_validate({
#                 "bid": bid,
#                 "tokens": tokens,
#                 "expires_at": expires_at,
#                 "status": status
#             })
#             self.global_state.batches[bid] = state
#         finally:
#             self.lock.release()
#             self.save()
#
#     @staticmethod
#     def get_instance():
#         if not GptBatchTracker.__instance:
#             GptBatchTracker.__instance = GptBatchTracker()
#         return GptBatchTracker.__instance
