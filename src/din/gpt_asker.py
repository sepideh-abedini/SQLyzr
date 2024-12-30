import asyncio
import json
import os

from openai import AsyncClient

from src.util.logger import log


class GptAsker:
    # model = "gpt-4o-mini"
    model = "gpt-3.5-turbo"

    def __init__(self):
        self.client = AsyncClient(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=5
        )


class AsyncGptAsker(GptAsker):
    rps = 4

    async def ask_message(self, message, **kwargs):
        log("Sending GPT Request")
        result = await self.client.chat.completions.create(
            messages=[message],
            model=self.model,
            n=1,
            stream=False,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            **kwargs
        )
        log("Received GPT Response")
        return result

    async def ask_file(self, in_path: str, out_path: str, **kwargs):
        in_file = open(in_path)
        futures = []
        for line in in_file.readlines():
            message = json.loads(line)
            future = self.ask_message(message, **kwargs)
            futures.append(future)
        in_file.close()

        responses = []
        while len(futures) > 0:
            max_idx = min(len(futures), self.rps)
            temp = futures[:max_idx]
            futures = futures[max_idx:]
            temp_responses = await asyncio.gather(*temp)
            responses.extend(temp_responses)

        out_file = open(out_path, "w")
        for response in responses:
            out_file.write(f"{response.json()}\n")
        out_file.close()
