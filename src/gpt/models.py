from typing import Literal, Optional, TypedDict, List

import tiktoken
from openai import BaseModel
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice


class SQLyzrChoice(Choice):
    finish_reason: Optional[str]


class GptMessage(BaseModel):
    role: Literal['user', 'system']
    content: str


class RequestBody(BaseModel):
    model: str
    messages: list[GptMessage]
    max_completion_tokens: Optional[int] = None
    stop: list[str] = []
    n: int = 1
    # stream: bool = False
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class ExtraParams(TypedDict):
    model: Literal['gpt-4o-min', 'gpt-3.5-turbo']


class SqlyzrChatCompletion(ChatCompletion):
    choices: List[SQLyzrChoice]


class BatchInputResponse(ChatCompletion):
    finished: int
    choices: List[SQLyzrChoice]

    @classmethod
    def from_obj(cls, c: SqlyzrChatCompletion, **kwargs):
        return cls(**c.model_dump(), **kwargs)


class BatchInputRequest(BaseModel):
    custom_id: str
    method: Literal['POST'] = 'POST'
    url: Literal['/v1/chat/completions'] = '/v1/chat/completions'
    body: RequestBody

    @staticmethod
    def create_prompt_req(custom_id: str, prompt: str, extra_params: ExtraParams):
        body = {
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }
        body.update(extra_params)
        return BatchInputRequest.model_validate(
            {
                "custom_id": custom_id,
                "body": body
            }
        )

    def get_token_usage(self):
        try:
            encoding = tiktoken.encoding_for_model(self.body.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        total_tokens = 0
        for msg in self.body.messages:
            total_tokens = len(encoding.encode(msg.content))
        if self.body.max_completion_tokens:
            total_tokens += self.body.max_completion_tokens
        return total_tokens


class BatchResponse(BaseModel):
    body: SqlyzrChatCompletion


class BatchRequestOutput(BaseModel):
    custom_id: str
    response: BatchResponse

    @staticmethod
    def get_total_token_usage(responses: List['BatchRequestOutput']) -> int:
        total_tokens = 0
        for res in responses:
            total_tokens += res.response.body.usage.total_tokens
        return total_tokens
