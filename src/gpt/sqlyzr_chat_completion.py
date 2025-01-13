from openai.types.chat import ChatCompletion


class SqlyzrChatCompletion(ChatCompletion):
    completed_at: int
