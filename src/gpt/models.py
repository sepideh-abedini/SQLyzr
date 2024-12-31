from typing import Literal

from openai import BaseModel


class GptMessage(BaseModel):
    role: Literal['user', 'system']
    content: str


class RequestBody(BaseModel):
    model: Literal["gpt-4o-mini"] = "gpt-4o-mini"
    messages: list[GptMessage]


class BatchInputRequest(BaseModel):
    custom_id: str
    method: Literal['POST'] = 'POST'
    url: Literal['/v1/chat/completions'] = '/v1/chat/completions'
    body: RequestBody


def main():
    file = open("data/batch/reqs.jsonl")
    for line in file.readlines():
        person = BatchInputRequest.model_validate_json(line)
        print(person)


if __name__ == '__main__':
    main()
