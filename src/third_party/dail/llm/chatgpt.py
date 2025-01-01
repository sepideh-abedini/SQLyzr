import json.decoder

import openai
from src.third_party.dail.utils.enums import LLM
import time


def init_chatgpt(OPENAI_API_KEY, OPENAI_GROUP_ID, model):
    # if model == LLM.TONG_YI_QIAN_WEN:
    #     import dashscope
    #     dashscope.api_key = OPENAI_API_KEY
    # else:
    #     openai.api_key = OPENAI_API_KEY
    #     openai.organization = OPENAI_GROUP_ID
    openai.api_key = OPENAI_API_KEY
    openai.organization = OPENAI_GROUP_ID


def ask_completion(model, batch, temperature):
    response = openai.Completion.create(
        model=model,
        prompt=batch,
        temperature=temperature,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=[";"]
    )
    response_clean = [_["text"] for _ in response["choices"]]
    return dict(
        response=response_clean,
        **response["usage"]
    )


def ask_chat(model, messages: list, temperature, n):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=200,
        n=n
    )
    response_clean = [choice["message"]["content"] for choice in response["choices"]]
    if n == 1:
        response_clean = response_clean[0]
    return dict(
        response=response_clean,
        **response["usage"]
    )


def ask_llm(model: str, question: str, temperature: float, n: int):
    messages = [{"role": "user", "content": question}]
    response = ask_chat(model, messages, temperature, n)
    # response['response'] = [response['response']]

    return response
