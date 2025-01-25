from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.gateway.batch.batch_gateway import GptBatchGateway
from src.gpt.models import SqlyzrChatCompletion


class GptBatchFileSender(GptFileSender):
    __gateway: GptBatchGateway

    def __init__(self):
        self.__gateway = GptBatchGateway()

    async def _send_file(self, in_path: str) -> list[SqlyzrChatCompletion]:
        output = await self.__gateway.send_batch(in_path)
        result = list(map(lambda o: o.response.body, output))
        return result
