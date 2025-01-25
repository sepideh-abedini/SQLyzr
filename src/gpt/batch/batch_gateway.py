import datetime
import json
import os.path
import os.path
from os.path import basename
from typing import List

import backoff
from natsort import natsorted
from openai.types import Batch

from src.gpt.batch.batch_client import GptBatchClient
from src.gpt.batch.batch_info import BatchInfo
from src.gpt.batch.batch_tracker import BatchTracker
from src.gpt.gateway_exceptions import GptBatchFailedException, GptBatchNotCompletedException, GptRateLimitException
from src.gpt.models import BatchRequestOutput
from src.util.logger import debug_log, log


def on_rate_limit(details):
    log(f"Hit rate limit, retrying!")


def on_failed(details):
    log(details)
    log(f"Batch failed, retrying!")


def on_not_complete(details):
    debug_log(f"Batch not completed yet, retrying!")


class GptBatchGateway:
    client: GptBatchClient
    tracker: BatchTracker

    def __init__(self):
        self.client = GptBatchClient()
        self.tracker = BatchTracker.get_instance()
        self.pbar = None
        self.update = None

    async def upload_file(self, info: BatchInfo):
        if info.get_value("fid"):
            debug_log(f"[{info.in_path}]:\tFile exists")
        else:
            file_name = os.path.basename(info.in_path)
            file_content = open(info.in_path, "rb")
            response = self.client.create_file(file_name, file_content, "batch")
            info.set_value("fid", response.id)
            log(f"File created for {info.in_path}")

    async def retrieve_batch(self, info: BatchInfo) -> Batch:
        bid = info.get_value("bid")
        response = self.client.retrieve_batch(bid)
        return response

    async def download_batch_output(self, info: BatchInfo) -> List[BatchRequestOutput]:
        content = self.client.retrieve_file_content(info.get_value("oid"))
        with open(f"{info.in_path}.outfile.jsonl", "w") as file:
            file.write(content)
        responses = []
        for line in content.strip().split("\n"):
            response = BatchRequestOutput.model_validate_json(line)
            responses.append(response)
        responses = natsorted(responses, key=lambda r: r.custom_id)
        return responses

    async def create_batch_if_not_exist(self, info: BatchInfo):
        if info.get_value("bid"):
            debug_log(f"[{info.in_path}]:\tBatch exists")
        else:
            await self.tracker.init_batch(info.in_path)
            response = self.client.create_batch(info.get_value("fid"))
            bid = response.id
            info.set_value("bid", bid)
            log(f"Batch created: {basename(info.in_path)}")
            self.tracker.commit_batch(info.in_path, bid)

    async def retrieve_out_file_id(self, info: BatchInfo):
        if info.get_value("oid"):
            debug_log(f"[{info.in_path}]:\tOut file exists")
        else:
            batch = await self.retrieve_batch(info)
            log(f"\rBatch [{basename(info.in_path)}]: \t Status: {batch.status} Completion: {batch.request_counts.completed}/{batch.request_counts.total}")
            status = batch.status
            if status != "completed":
                if status == "failed":
                    batch_id = info.get_value("bid")
                    info.set_value("bid", None)
                    raise GptBatchFailedException(f"Batch job failed for {info.in_path} ==> {batch_id}")
                elif status == "expired":
                    batch_id = info.get_value("bid")
                    info.set_value("bid", None)
                    raise GptBatchFailedException(f"Batch expired for {info.in_path} ==> {batch_id}")
                else:
                    raise GptBatchNotCompletedException()
            log(f"Batch {basename(info.in_path)} completed!")
            info.set_value("oid", batch.output_file_id)

    def save_responses(self, responses: List[BatchRequestOutput], info: BatchInfo):
        with open(f"{info.in_path}.out.jsonl", "w") as file:
            for response in responses:
                file.write(f"{response.json()}\n")

    def get_in_prog_batches(self):
        batches = self.client.list_batches()
        batches = list(filter(lambda b: b.status != "completed" and b.status != "failed", batches))
        return batches

    async def update_tokens_usage(self, info: BatchInfo):
        await self.tracker.init_batch(info.in_path)
        self.tracker.commit_batch(info.in_path, info.get_value("bid"))

    async def save_batch_stats(self, info: BatchInfo):
        batch = await self.retrieve_batch(info)
        with open(f"{info.in_path}.batch.stats.json", "w") as file:
            file.write(json.dumps(batch.dict(), indent=4))
        return batch

    def get_total_token_usage(self, responses: List[BatchRequestOutput]) -> int:
        total_tokens = 0
        for res in responses:
            total_tokens += res.response.body.usage.total_tokens
        return total_tokens

    @backoff.on_exception(backoff.constant, on_backoff=on_rate_limit, interval=10, max_tries=50,
                          exception=GptRateLimitException)
    @backoff.on_exception(backoff.constant, on_backoff=on_failed, interval=10, max_tries=50,
                          exception=GptBatchFailedException)
    @backoff.on_exception(backoff.constant, on_backoff=on_not_complete, interval=10, max_tries=None,
                          exception=GptBatchNotCompletedException)
    async def send_batch(self, in_path: str) -> List[BatchRequestOutput]:
        info = BatchInfo(in_path)

        await self.upload_file(info)

        await self.create_batch_if_not_exist(info)

        await self.retrieve_out_file_id(info)

        responses = await self.download_batch_output(info)

        await self.save_batch_stats(info)

        return responses
