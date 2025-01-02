from typing import Literal, Optional, Dict
import tiktoken

from openai import BaseModel
from openai.types.chat import ChatCompletion


class GptMessage(BaseModel):
    role: Literal['user', 'system']
    content: str


class RequestBody(BaseModel):
    model: Literal["gpt-4o-mini", "gpt-3.5-turbo"]
    messages: list[GptMessage]
    max_completion_tokens: Optional[int] = None
    stop: list[str] = []
    n: int = 1
    # stream: bool = False
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class BatchInputRequest(BaseModel):
    custom_id: str
    method: Literal['POST'] = 'POST'
    url: Literal['/v1/chat/completions'] = '/v1/chat/completions'
    body: RequestBody

    @staticmethod
    def create_prompt_req(custom_id: str, model: str, prompt: str, extra_params: Dict):
        body = {
            "model": model,
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
        encoding = tiktoken.encoding_for_model(self.body.model)
        total_tokens = 0
        for msg in self.body.messages:
            total_tokens = len(encoding.encode(msg.content))
        return total_tokens


class BatchResponse(BaseModel):
    body: ChatCompletion


class BatchRequestOutput(BaseModel):
    custom_id: str
    response: BatchResponse
