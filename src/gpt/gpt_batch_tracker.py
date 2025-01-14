import asyncio
import json
import os.path
from asyncio import Lock
from typing import Dict, Literal

from openai.types import Batch

from src.gpt.gpt_client import GptBatchClient
from src.gpt.gpt_gateway import GptRateLimitException
from src.gpt.gpt_limits import GptRateLimits
from src.gpt.models import BatchInputRequest
from src.util.logger import debug_log, log


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
    __instance: 'BatchTracker' = None
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
        log(f"Current token usage: {self.total_tokens()}/{self.limits.batch_tokens_per_day}")

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
        expired_bids = []
        for bid in self.batch_tokens.keys():
            if bid not in cur_bids:
                expired_bids.append(bid)
        for bid in expired_bids:
            self.batch_tokens.pop(bid)

    def should_count(self, batch: Batch) -> bool:
        if not batch.in_progress_at and batch.status != "validating":
            return False
        return True

    def total_tokens(self) -> int:
        cur_batches = self.batch_client.list_cur_batches()
        cur_batches = filter(self.should_count, cur_batches)
        tokens = 0
        max_tokens = max(self.batch_tokens.values(), default=0)
        for batch in cur_batches:
            if batch.id in self.batch_tokens:
                tokens += self.batch_tokens[batch.id]
            else:
                log(f"Warning! Batch not exists in stored state: {batch.id}")
                tokens += max_tokens
        return tokens

    def tokens_exceed_limit(self, tokens: int):
        total_tokens = self.total_tokens()
        new_total = tokens + total_tokens
        debug_log(f"Checking Token Limit: {tokens}+{total_tokens} = {new_total} /{self.limits.batch_tokens_per_day}")
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
            if bid in self.batch_tokens:
                debug_log(f"Updating tokens usage: {self.batch_tokens[bid]} => {tokens}")
            self.batch_tokens[bid] = tokens
        finally:
            self.lock.release()
            self.save()

    @staticmethod
    def get_instance():
        if not BatchTracker.__instance:
            BatchTracker.__instance = BatchTracker()
        return BatchTracker.__instance
