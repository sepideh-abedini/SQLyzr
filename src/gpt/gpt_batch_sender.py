from typing import List

from openai.types.chat import ChatCompletion

from src.gpt.gpt_from_file_sender import GptSingleSender, GptFromFileSender


class GptBatchSender(GptFromFileSender):

    async def send_from_file(self, in_path: str, out_path: str):
        resps = self.send_batch(in_path)
        self.save_res_to_file(resps, out_path)

    def send_batch(self, in_path: str) -> List[ChatCompletion]:
        state = BatchState(f"{in_path}.state.json")

        if not state.file_id:
            file_name = os.path.basename(in_path)
            file_content = open(in_path, "rb")
            try:
                response = self.client.create_file(file_name, file_content, "batch")
                state.file_id = response.id
                log(response)
                print(f"File uploaded {in_path} => {state.file_id}")
            except APIError as e:
                print(f"Failed to upload batch request file: {in_path}")
                raise e

        if not state.batch_id:
            try:
                response = self.client.create_batch_if_not_exist(state.file_id)
                state.batch_id = response.id
                log(response)
                print(f"Batch job created: {state.batch_id}")
            except APIError as e:
                print(f"Failed to create batch job\n{e}")
                raise e

        if not state.out_file_id:
            try:
                response = self.client.retrieve_batch(state.batch_id)
                while response.status != "completed":
                    print(f"Batch job: {state.batch_id} not completed yet! Current status: {response.status}")
                    print("Polling for job status")
                    await asyncio.sleep(5)
                    try:
                        response = self.client.retrieve_batch(state.batch_id)
                    except APIError as e:
                        print(f"Failed to retrieve job status\n{e}")
                        raise e
                print(f"Batch job: {state.batch_id} completed! out_file_id: {response.output_file_id}")
                state.out_file_id = response.output_file_id
            except APIError as e:
                print(f"Failed to retrieve batch job\n{e}")
                raise e

        try:
            content = self.client.retrieve_file_content(state.out_file_id)
            responses = []
            for line in content.strip().split("\n"):
                response = BatchRequestOutput.model_validate_json(line)
                responses.append(response)
            responses = sorted(responses, key=lambda r: r.custom_id)
            responses = list(map(lambda r: r.response.body, responses))
            return responses
        except APIError as e:
            print(f"Failed to retrieve output file\n{e}")
            raise e
