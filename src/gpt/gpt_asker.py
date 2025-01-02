import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass

from openai.types.chat import ChatCompletion
from pydantic import BaseModel
import json
import os
from typing import Type, Optional, TypeVar

from openai import AsyncClient, APIError

from src.gpt.gpt_client import GptBatchClient
from src.gpt.models import BatchInputRequest, BatchRequestOutput
from src.util.logger import log


class GptAsker(ABC):
    async def ask_file(self, in_path: str, out_path: str):
        responses = await self.get_responses(in_path)
        self.save_responses(responses, out_path)

    @abstractmethod
    async def get_responses(self, in_path: str) -> list[ChatCompletion]:
        pass

    def save_responses(self, responses: list[ChatCompletion], out_path: str):
        out_file = open(out_path, "w")
        for response in responses:
            out_file.write(f"{response.json()}\n")
        out_file.close()


class BatchState:
    path: str
    file_id: Optional[str] = None
    batch_id: Optional[str] = None
    out_file_id: Optional[str] = None

    def __init__(self, path: str):
        if os.path.exists(path):
            with open(path) as file:
                saved_state = json.loads(file.read())
                for key in saved_state:
                    setattr(self, key, saved_state[key])
        self.path = path

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        self.save()

    def __str__(self):
        return str(self.__dict__)

    def save(self):
        with open(self.path, "w") as file:
            file.write(json.dumps(self.__dict__))


class BatchGptAsker(GptAsker):

    def __init__(self):
        self.client = GptBatchClient()

    async def get_responses(self, in_path: str) -> list[ChatCompletion]:
        state = BatchState(f"{in_path}.state.json")

        if not state.file_id:
            file_name = os.path.basename(in_path)
            file_content = open(in_path, "rb")
            try:
                response = self.client.create_file(file_name, file_content, "batch")
                state.file_id = response.id
                log(response)
                print(f"File uploaded {in_path} => {state.file_id}")
            except APIError as e:
                print(f"Failed to upload batch request file: {in_path}")
                raise e

        if not state.batch_id:
            try:
                response = self.client.create_batch(state.file_id)
                state.batch_id = response.id
                log(response)
                print(f"Batch job created: {state.batch_id}")
            except APIError as e:
                print(f"Failed to create batch job\n{e}")
                raise e

        if not state.out_file_id:
            try:
                response = self.client.retrieve_batch(state.batch_id)
                while response.status != "completed":
                    print(f"Batch job: {state.batch_id} not completed yet! Current status: {response.status}")
                    print("Polling for job status")
                    await asyncio.sleep(5)
                    try:
                        response = self.client.retrieve_batch(state.batch_id)
                    except APIError as e:
                        print(f"Failed to retrieve job status\n{e}")
                        raise e
                print(f"Batch job: {state.batch_id} completed! out_file_id: {response.output_file_id}")
                state.out_file_id = response.output_file_id
            except APIError as e:
                print(f"Failed to retrieve batch job\n{e}")
                raise e

        try:
            content = self.client.retrieve_file_content(state.out_file_id)
            responses = []
            for line in content.strip().split("\n"):
                response = BatchRequestOutput.model_validate_json(line)
                responses.append(response)
            responses = sorted(responses, key=lambda r: r.custom_id)
            responses = list(map(lambda r: r.response.body, responses))
            return responses
        except APIError as e:
            print(f"Failed to retrieve output file\n{e}")
            raise e


class AsyncGptAsker(GptAsker):
    client: AsyncClient
    rps = 4

    def __init__(self):
        self.client = AsyncClient(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=5
        )

    async def process_request(self, request: BatchInputRequest):
        log("Sending GPT Request")
        result = await self.client.chat.completions.create(
            **request.body.dict()
        )
        log("Received GPT Response")
        return result

    async def get_responses(self, in_path: str) -> list[ChatCompletion]:
        in_file = open(in_path)
        futures = []
        for line in in_file.readlines():
            message = BatchInputRequest.model_validate_json(line)
            future = self.process_request(message)
            futures.append(future)
        in_file.close()

        responses = []
        while len(futures) > 0:
            max_idx = min(len(futures), self.rps)
            temp = futures[:max_idx]
            futures = futures[max_idx:]
            temp_responses = await asyncio.gather(*temp)
            responses.extend(temp_responses)
        return responses


T = TypeVar('T', bound=BaseModel)


class AsyncGptFormattedAsker(AsyncGptAsker):
    response_format: Type[T]

    def __init__(self, response_format: Type[T]):
        super().__init__()
        self.response_format = response_format

    async def process_request(self, request: BatchInputRequest) -> T:
        log("Sending formatted GPT Request")
        result = await self.client.beta.chat.completions.parse(
            response_format=self.response_format,
            **request.body.dict()
        )
        return result
