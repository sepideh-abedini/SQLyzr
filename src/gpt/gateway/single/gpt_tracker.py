import asyncio
import os
from asyncio import Lock
from typing import List

from src.gpt.gateway.single.gpt_limits import GptRateLimits, LIMITS
from src.gpt.gateway.single.gpt_usage import GptTokenUsage
from src.util.logger import debug_log, log


class GptUsageTracker:
    __instance: 'GptUsageTracker' = None
    __limits: GptRateLimits

    __usage: List[GptTokenUsage]
    __reqs: int
    __total_tokens: int
    __lock: Lock

    def __init__(self):
        self.__usage = []
        self.__total_tokens = 0
        self.__lock = asyncio.Lock()
        self.__limits = LIMITS[os.environ.get("OPENAI_USAGE_TIER", "tier1")]
        self.__reqs = 0

    @property
    def total_tokens(self):
        return self.__total_tokens

    async def check_limit(self, tokens: int):
        await self.__lock.acquire()
        try:
            self.__update_total_tokens()
            debug_log(f"Checking Token Limit: {tokens}+{self.__total_tokens}/{self.__limits.tokens_per_min}")
            if tokens + self.__total_tokens > self.__limits.tokens_per_min:
                log(f"Exceeding token limit: {tokens}+{self.__total_tokens}/{self.__limits.tokens_per_min}")
                return False
            debug_log(f"Checking RPM Limit: {self.__reqs}/{self.__limits.req_per_min}")
            if self.__reqs + 1 >= self.__limits.req_per_min:
                log(f"Exceeding RPM limit: {self.__reqs}/{self.__limits.req_per_min}")
                return False
            return True
        finally:
            self.__lock.release()

    async def add_usage(self, tokens: int):
        await self.__lock.acquire()
        try:
            usage = GptTokenUsage(tokens)
            old_total = self.__total_tokens
            old_req = self.__reqs
            self.__usage.append(usage)
            self.__total_tokens += usage.tokens
            self.__reqs += 1
            debug_log(f"Token usage added: {old_total} => {self.__total_tokens}")
            debug_log(f"Request added: {old_req} => {self.__reqs}")
            return usage
        finally:
            self.__lock.release()

    def __update_total_tokens(self):
        while len(self.__usage) > 0:
            usage = self.__usage[0]
            if not usage.expired():
                break
            old_tokens = self.__total_tokens
            old_reqs = self.__reqs
            self.__total_tokens -= usage.tokens
            self.__reqs -= 1
            self.__usage.pop(0)
            debug_log(f"Expired token: {usage.tokens}, {old_tokens} => {self.__total_tokens}")
            debug_log(f"Expired req: {old_reqs} => {self.__reqs}")

    @staticmethod
    def get_instance():
        if not GptUsageTracker.__instance:
            GptUsageTracker.__instance = GptUsageTracker()
        return GptUsageTracker.__instance
