import os.path
import os.path
from typing import List, Literal, Optional

import backoff

from src.gpt.gpt_batch_tracker import BatchTracker
from src.gpt.gpt_client import GptBatchClient
from src.gpt.gpt_gateway import GptRateLimitException, GptBatchNotCompletedException, \
    GptBatchFailedException
from src.gpt.models import BatchRequestOutput


def on_rate_limit(details):
    print(f"Hit rate limit, retrying!")


def on_failed(details):
    print(f"Batch failed, retrying!")


def on_not_complete(details):
    print(f"Batch not completed yet, retrying!")


BatchInfoProps = Literal["fid", "bid", "oid"]


class BatchInfo:
    in_path: str

    def __init__(self, in_path: str):
        self.in_path = in_path

    def __file_path(self, key: BatchInfoProps):
        return f"{self.in_path}.{key}"

    def get_value(self, key: BatchInfoProps):
        if os.path.exists(self.__file_path(key)):
            with open(self.__file_path(key)) as file:
                return file.read()
        else:
            return None

    def set_value(self, key: BatchInfoProps, value: Optional[str]):
        if not value:
            if os.path.exists(self.__file_path(key)):
                os.remove(self.__file_path(key))
        else:
            with open(self.__file_path(key), "w") as file:
                file.write(value)


class GptBatchGateway:
    client: GptBatchClient
    tracker: BatchTracker

    def __init__(self):
        self.client = GptBatchClient()
        self.tracker = BatchTracker.get_instance()

    async def upload_file(self, info: BatchInfo):
        if info.get_value("fid"):
            print(f"[{info.in_path}]:\tFile exists")
        else:
            file_name = os.path.basename(info.in_path)
            file_content = open(info.in_path, "rb")
            response = self.client.create_file(file_name, file_content, "batch")
            info.set_value("fid", response.id)

    async def retrieve_batch(self, info: BatchInfo):
        bid = info.get_value("bid")
        response = self.client.retrieve_batch(bid)
        return response

    async def download_batch_output(self, info: BatchInfo) -> List[BatchRequestOutput]:
        content = self.client.retrieve_file_content(info.get_value("oid"))
        responses = []
        for line in content.strip().split("\n"):
            response = BatchRequestOutput.model_validate_json(line)
            responses.append(response)
        responses = sorted(responses, key=lambda r: r.custom_id)
        return responses

    async def create_batch_if_not_exist(self, info: BatchInfo):
        if info.get_value("bid"):
            print(f"[{info.in_path}]:\tBatch exists")
        else:
            await self.tracker.init_batch(info.in_path)
            response = self.client.create_batch(info.get_value("fid"))
            bid = response.id
            info.set_value("bid", bid)
            print(f"Batch created: {bid}")
            self.tracker.commit_batch(info.in_path, bid)

    async def retrieve_out_file_id(self, info: BatchInfo):
        if info.get_value("oid"):
            print(f"[{info.in_path}]:\tOut file exists")
        else:
            batch = await self.retrieve_batch(info)
            status = batch.status
            if status != "completed":
                if status == "failed":
                    batch_id = info.get_value("bid")
                    info.set_value("bid", None)
                    raise GptBatchFailedException(f"Batch job failed for {info.in_path} ==> {batch_id}")
                else:
                    raise GptBatchNotCompletedException()
            info.set_value("oid", batch.output_file_id)

    def save_responses(self, responses: List[BatchRequestOutput], info: BatchInfo):
        with open(f"{info.in_path}.out.jsonl", "w") as file:
            for response in responses:
                file.write(f"{response.json()}\n")

    def get_in_prog_batches(self):
        batches = self.client.list_batches()
        batches = list(filter(lambda b: b.status != "completed" and b.status != "failed", batches))
        return batches

    @backoff.on_exception(backoff.constant, on_backoff=on_rate_limit, interval=10, max_tries=50,
                          exception=GptRateLimitException)
    @backoff.on_exception(backoff.constant, on_backoff=on_failed, interval=10, max_tries=50,
                          exception=GptBatchFailedException)
    @backoff.on_exception(backoff.constant, on_backoff=on_not_complete, interval=10, max_tries=60,
                          exception=GptBatchNotCompletedException)
    async def send_batch(self, in_path: str) -> List[BatchRequestOutput]:
        info = BatchInfo(in_path)

        await self.upload_file(info)
        print(f"[{in_path}]:\tFile uploaded")

        await self.create_batch_if_not_exist(info)
        print(f"[{in_path}]:\tBatch created")

        await self.retrieve_out_file_id(info)
        print(f"[{in_path}]:\tOutput File id retrieved")

        responses = await self.download_batch_output(info)
        print(f"[{in_path}]:\tOutfile downloaded")

        return responses
