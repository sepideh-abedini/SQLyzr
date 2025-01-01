import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass

from openai.types.chat import ChatCompletion
from pydantic import BaseModel
import json
import os
from typing import Type, Optional

from openai import AsyncClient, APIError

from src.gpt.gpt_client import GptBatchClient
from src.gpt.models import BatchInputRequest
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
    file_id: Optional[str]

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

    def load_state(self, in_path: str) -> BatchState:
        state_path = f"{in_path}.state.json"
        file = open(state_path)
        state = json.loads(file.read())

    async def get_responses(self, in_path: str) -> list[ChatCompletion]:
        state = self.load_state(in_path)

        if not state.file_id:
            file_name = os.path.basename(in_path)
            file_content = open(in_path, "rb")
            try:
                response = self.client.create_file(file_name, file_content, "batch")
                state.file_id = response.id
                print("File uploaded")
                state.file_id = response
                log(response)
            except APIError as e:
                log(e)
                print(f"Failed to upload batch request file: {in_path}")
        print("Batch file uploaded:")


class AsyncGptAsker(GptAsker):
    client: AsyncClient
    model: str
    rps = 4

    def __init__(self, model):
        self.model = model
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


class AsyncGptFormattedAsker(AsyncGptAsker):
    response_format: Type[BaseModel]

    def __init__(self, model, response_format: Type[BaseModel]):
        super().__init__(model)
        self.response_format = response_format

    async def process_request(self, message, **kwargs):
        log("Sending formatted GPT Request")
        result = await self.client.beta.chat.completions.parse(
            model=self.model,
            n=1,
            messages=[message],
            response_format=self.response_format,
            **kwargs
        )
        return result
