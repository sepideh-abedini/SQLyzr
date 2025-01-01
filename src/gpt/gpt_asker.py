import asyncio
from pydantic import BaseModel
import json
import os
from typing import Type

from openai import AsyncClient

from src.gpt.models import BatchInputRequest
from src.util.logger import log


class GptAsker:
    client: AsyncClient
    model: str

    def __init__(self, model):
        self.model = model
        self.client = AsyncClient(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=5
        )


class AsyncGptAsker(GptAsker):
    rps = 4

    async def process_request(self, request: BatchInputRequest):
        log("Sending GPT Request")
        result = await self.client.chat.completions.create(
            **request.body.dict()
        )
        log("Received GPT Response")
        return result

    async def ask_file(self, in_path: str, out_path: str):
        responses = await self.get_responses(in_path)
        self.save_responses(responses, out_path)

    def save_responses(self, responses, out_path: str):
        out_file = open(out_path, "w")
        for response in responses:
            out_file.write(f"{response.json()}\n")
        out_file.close()

    async def get_responses(self, in_path: str):
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

    def save_responses(self, responses, out_path: str):
        out_file = open(out_path, "w")
        for response in responses:
            out_file.write(f"{response.json()}\n")
        out_file.close()
