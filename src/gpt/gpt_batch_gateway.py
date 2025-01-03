import asyncio
import os.path
import random
import uuid
from typing import Optional

import backoff

from src.gpt.gpt_batch_tracker import GptBatchTracker, BatchJobState
from src.gpt.gpt_client import GptBatchClient
from src.gpt.gpt_gateway import GptGatewayException, GptRateLimitException, GptBatchNotCompletedException
from src.gpt.gpt_tracker import GptUsageTracker
from src.gpt.models import BatchInputRequest


def on_rate_limit(details):
    print(f"Hit rate limit, retrying!")


class GptBatchGateway:
    client: GptBatchClient
    tracker: GptBatchTracker

    def __init__(self):
        self.client = GptBatchClient()
        self.tracker = GptBatchTracker.get_instance()

    async def upload_file(self, state: BatchJobState):
        if state.file_id:
            print(f"[{state.in_path}]:\tFile exists")
        else:
            await asyncio.sleep(random.randint(3, 10))
            state.file_id = "BAR_FILE"
            await self.tracker.set_state(state)

    async def get_batch_status(self, state: BatchJobState):
        await asyncio.sleep(random.randint(4, 6))
        return "completed"

    async def download_batch_output(self, state: BatchJobState):
        await asyncio.sleep(1)

    async def create_batch_if_not_exist(self, state: BatchJobState):
        if state.batch_id:
            print(f"[{state.in_path}]:\tBatch exists")
        else:
            await asyncio.sleep(random.randint(3, 5))
            state.batch_id = str(uuid.uuid4())
            await self.tracker.set_state(state)
            print(f"Batch created: {state.batch_id}")

    async def retrieve_out_file_id(self, state: BatchJobState):
        if state.out_file_id:
            print(f"[{state.in_path}]:\tOut file exists")
        else:
            status = await self.get_batch_status(state)
            if status != "completed":
                if status == "failed":
                    batch_id = state.batch_id
                    del state.batch_id
                    await self.tracker.set_state(state)
                    raise GptGatewayException(f"Batch job failed: {batch_id}")
                else:
                    raise GptBatchNotCompletedException()
            state.out_file_id = "BAR_OUT_FILE"
            await self.tracker.set_state(state)

    # @backoff.on_exception(backoff.constant, on_backoff=on_rate_limit, interval=10, max_tries=5,
    #                       exception=GptRateLimitException)
    async def send_batch(self, in_path: str):
        state = await self.tracker.get_state(in_path)

        await self.upload_file(state)

        await self.create_batch_if_not_exist(state)

        await self.retrieve_out_file_id(state)

        await self.download_batch_output(state)
