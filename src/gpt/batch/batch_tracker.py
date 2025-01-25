import asyncio
import json
import os.path
from asyncio import Lock
from typing import Dict, Literal

from openai.types import Batch

from src.gpt.batch.batch_client import GptBatchClient
from src.gpt.gateway.gateway_exceptions import GptRateLimitException
from src.gpt.models import BatchInputRequest
from src.gpt.tracker.gpt_limits import GptRateLimits, LIMITS
from src.util.logger import debug_log, log
from src.util.model_utils import read_jsonl


def get_req_file_token_usage(in_path: str):
    reqs = read_jsonl(in_path, BatchInputRequest)
    total_tokens = 0
    for req in reqs:
        total_tokens += req.get_token_usage()
    return total_tokens


BatchStatus = Literal[
    "validating", "failed", "in_progress", "finalizing", "completed", "expired", "cancelling", "cancelled"]


class BatchTracker:
    __instance: 'BatchTracker' = None
    __batch_client: GptBatchClient
    __batch_tokens: Dict[str, int]
    __save_path: str = ".batch.tokens.json"
    __limits: GptRateLimits
    __lock: Lock

    def __init__(self):
        self.__batch_client = GptBatchClient()
        self.__load()
        self.__lock = asyncio.Lock()
        self.__limits = LIMITS[os.environ.get("OPENAI_USAGE_TIER", "tier1")]
        log(f"Current token usage: {self.__total_tokens()}/{self.__limits.batch_tokens_per_day}")

    async def init_batch(self, in_path):
        await self.__lock.acquire()
        tokens = get_req_file_token_usage(in_path)
        if self.__tokens_exceed_limit(tokens):
            self.__lock.release()
            raise GptRateLimitException()

    def commit_batch(self, in_path: str, bid: str):
        try:
            tokens = get_req_file_token_usage(in_path)
            if bid in self.__batch_tokens:
                debug_log(f"Updating tokens usage: {self.__batch_tokens[bid]} => {tokens}")
            self.__batch_tokens[bid] = tokens
        finally:
            self.__lock.release()
            self.__save()

    def __save(self):
        with open(self.__save_path, "w") as file:
            file.write(json.dumps(self.__batch_tokens, indent=4))

    def __load(self):
        if not os.path.exists(self.__save_path):
            self.__batch_tokens = dict()
            self.__save()

        cur_batches = self.__batch_client.list_cur_batches()
        cur_bids = set(map(lambda b: b.id, cur_batches))
        with open(self.__save_path) as file:
            self.__batch_tokens = json.load(file)
        expired_bids = []
        for bid in self.__batch_tokens.keys():
            if bid not in cur_bids:
                expired_bids.append(bid)
        for bid in expired_bids:
            self.__batch_tokens.pop(bid)

    @staticmethod
    def __should_count(batch: Batch) -> bool:
        #  Never started                Being initialized
        if not batch.in_progress_at and batch.status != "validating":
            return False
        return True

    def __total_tokens(self) -> int:
        cur_batches = self.__batch_client.list_cur_batches()
        cur_batches = list(filter(self.__should_count, cur_batches))
        tokens = 0
        max_tokens = max(self.__batch_tokens.values(), default=0)
        for batch in cur_batches:
            if batch.id in self.__batch_tokens:
                tokens += self.__batch_tokens[batch.id]
            else:
                log(f"Warning! Batch not exists in stored state: {batch.id}")
                tokens += max_tokens
        return tokens

    def __tokens_exceed_limit(self, tokens: int):
        total_tokens = self.__total_tokens()
        new_total = tokens + total_tokens
        debug_log(f"Checking Token Limit: {tokens}+{total_tokens} = {new_total} /{self.__limits.batch_tokens_per_day}")
        if new_total > self.__limits.batch_tokens_per_day:
            log(f"Exceeding token limit: {tokens}+{total_tokens} = {new_total} /{self.__limits.batch_tokens_per_day}")
        return new_total > self.__limits.batch_tokens_per_day

    @staticmethod
    def get_instance():
        if not BatchTracker.__instance:
            BatchTracker.__instance = BatchTracker()
        return BatchTracker.__instance
