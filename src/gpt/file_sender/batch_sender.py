from openai.types.chat import ChatCompletion

from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.gateway.batch.batch_gateway import GptBatchGateway


class GptBatchFileSender(GptFileSender):
    __gateway: GptBatchGateway

    def __init__(self):
        super().__init__()
        self.__gateway = GptBatchGateway()

    async def _send_file(self, in_path: str) -> list[ChatCompletion]:
        output, usage = await self.__gateway.send_batch(in_path)
        self._tracker.add_usage(usage)
        result = list(map(lambda o: o.response.body, output))
        return result
