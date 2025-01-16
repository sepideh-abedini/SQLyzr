import asyncio
import os
from asyncio import Lock
from typing import List

from src.gpt.gpt_limits import GptRateLimits, LIMITS
from src.gpt.gpt_usage import GptUsage
from src.util.logger import debug_log, log


class GptUsageTracker:
    __instance: 'GptUsageTracker' = None
    limits: GptRateLimits

    __usage: List[GptUsage]
    reqs: int
    total_tokens: int
    lock: Lock

    def __init__(self):
        self.__usage = []
        self.total_tokens = 0
        self.lock = asyncio.Lock()
        self.limits = LIMITS[os.environ.get("OPENAI_USAGE_TIER", "tier1")]
        self.reqs = 0

    async def check_limit(self, tokens: int):
        await self.lock.acquire()
        try:
            self.__update_total_tokens()
            debug_log(f"Checking Token Limit: {tokens}+{self.total_tokens}/{self.limits.tokens_per_min}")
            if tokens + self.total_tokens > self.limits.tokens_per_min:
                log(f"Exceeding token limit: {tokens}+{self.total_tokens}/{self.limits.tokens_per_min}")
                return False
            debug_log(f"Checking RPM Limit: {self.reqs}/{self.limits.req_per_min}")
            if self.reqs + 1 >= self.limits.req_per_min:
                log(f"Exceeding RPM limit: {self.reqs}/{self.limits.req_per_min}")
                return False
            return True
        finally:
            self.lock.release()

    async def add_usage(self, tokens: int):
        await self.lock.acquire()
        try:
            usage = GptUsage(tokens)
            old_total = self.total_tokens
            old_req = self.reqs
            self.__usage.append(usage)
            self.total_tokens += usage.tokens
            self.reqs += 1
            debug_log(f"Token usage added: {old_total} => {self.total_tokens}")
            debug_log(f"Request added: {old_req} => {self.reqs}")
            return usage
        finally:
            self.lock.release()

    def __update_total_tokens(self):
        while len(self.__usage) > 0:
            usage = self.__usage[0]
            if not usage.expired():
                break
            old_tokens = self.total_tokens
            old_reqs = self.reqs
            self.total_tokens -= usage.tokens
            self.reqs -= 1
            self.__usage.pop(0)
            debug_log(f"Expired token: {usage.tokens}, {old_tokens} => {self.total_tokens}")
            debug_log(f"Expired req: {old_reqs} => {self.reqs}")

    @staticmethod
    def get_instance():
        if not GptUsageTracker.__instance:
            GptUsageTracker.__instance = GptUsageTracker()
        return GptUsageTracker.__instance
