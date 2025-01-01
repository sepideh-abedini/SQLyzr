from openai import BaseModel

from src.gpt.models import GptMessage, BatchInputRequest


def convert_message_to_req(message: GptMessage) -> BatchInputRequest:
    result = BatchInputRequest.model_validate({"custom_id": "1", "body": {"messages": [message]}})
    return result


def convert_message_file_to_req(in_path: str, out_path: str):
    in_file = open(in_path)
    out_file = open(out_path, "w")
    for line in in_file.readlines():
        msg = GptMessage.model_validate_json(line)
        req = convert_message_to_req(msg)
        out_file.write(f"{req.json()}\n")

    in_file.close()
    out_file.close()


