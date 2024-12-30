import json
from typing import List, Callable, Type, TypeVar

from openai.types.chat import ChatCompletion
from pydantic import BaseModel

ResponseProcessor = Callable[[int, str], str]


def load_responses(in_path: str) -> List[ChatCompletion]:
    file = open(in_path)
    data = []
    for line in file.readlines():
        response = json.loads(line)
        response = ChatCompletion.model_validate(response)
        data.append(response)
    return data


T = TypeVar('T', bound=BaseModel)


def identity_processor(i: int, content: T) -> T:
    return content


def process_responses(file_path: str, response_processor: ResponseProcessor = identity_processor) -> List[str]:
    responses = load_responses(file_path)
    results = []
    for i, response in enumerate(responses):
        content = response.choices[0].message.content
        processed = response_processor(i, content)
        results.append(processed)
    return results


U = TypeVar('U')


def process_formatted_responses(file_path: str, response_format: Type[T],
                                response_processor: Callable[[int, T], U] = identity_processor) -> List[U]:
    responses = load_responses(file_path)
    results = []
    for i, response in enumerate(responses):
        content = response_format.model_validate(response.choices[0].message.parsed)
        processed = response_processor(i, content)
        results.append(processed)
    return results
