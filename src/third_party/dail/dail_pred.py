import json
import os
from typing import Callable, List

from src.gpt.gpt_asker import GptAsker, BatchGptAsker, AsyncGptAsker
from src.gpt.gpt_utils import load_responses
from src.gpt.models import BatchInputRequest
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.data_preprocess import schema_linking_producer
from src.third_party.dail.generate_question import generate_questions
from src.third_party.dail.utils.post_process import process_duplication, get_sqls
from src.util.logger import log

BatchRequestGenerator = Callable[[int, str, str], BatchInputRequest]


class DailPredictor:
    conf: DailConfig
    gpt_asker: GptAsker

    def __init__(self, conf: DailConfig):
        self.conf = conf
        if self.conf.batch:
            self.gpt_asker = BatchGptAsker()
        else:
            self.gpt_asker = AsyncGptAsker()

    def create_batch_req(self, idx: str, prompt: str, extra_params):
        return BatchInputRequest.create_prompt_req(idx, self.conf.model, prompt, extra_params)

    def generate_batch_file(self):
        questions_json = json.load(open(self.conf.questions_path(), "r"))
        questions = [_["prompt"] for _ in questions_json["questions"]]
        file = open(self.conf.get_batch_path("in"), "w")
        for i, question in enumerate(questions):
            request = self.create_batch_req(f"i{i}", question, {"n": self.conf.self_consistent_set_size})
            file.write(f"{request.json()}\n")
        file.close()

    async def run(self):

        schema_linking_producer(self.conf)

        generate_questions(self.conf)
        
        self.generate_batch_file()

        await self.ask_file(self.conf.get_batch_path("in"), self.conf.get_batch_path("out"))

        sqls = await self.process_responses(self.conf.get_batch_path("out"))

        self.save_sqls(self.conf.run_conf.get_pred_path(), sqls)

        self.save_total_token_usage()

    def save_sqls(self, out_path, sqls: List[str]):
        file = open(out_path, 'w')
        for sql in sqls:
            file.write(f"{sql}\n")
        file.close()

    def get_token_usage(self, file_path: str):
        token_usage = []
        responses = load_responses(file_path)
        for response in responses:
            token_usage.append(response.usage.total_tokens)
        return token_usage

    def save_total_token_usage(self):
        all_usage = []
        for file in [
            self.conf.get_batch_path("out")
        ]:
            all_usage.append(self.get_token_usage(file))
        all_usage = [sum(usages) for usages in zip(*all_usage)]
        out_file = open(self.conf.run_conf.get_token_path(), "w")
        for usage in all_usage:
            out_file.write(f"{usage}\n")
        out_file.close()

    async def process_responses(self, file_path) -> List[str]:
        with open(self.conf.run_conf.dataset_config.get_data_path()) as data_file:
            data = json.load(data_file)
            db_ids = [example['db_id'] for example in data]
        responses = load_responses(file_path)
        results = []
        for i, response in enumerate(responses):
            contents = [choice.message.content for choice in response.choices]
            if self.conf.self_consistent_set_size == 1:
                for sql in contents:
                    sql = " ".join(sql.replace("\n", " ").split())
                    sql = process_duplication(sql)
                    if sql.startswith("SELECT"):
                        results.append(sql + "\n")
                    elif sql.startswith(" "):
                        results.append("SELECT" + sql + "\n")
                    else:
                        results.append("SELECT " + sql + "\n")
            else:
                db_id = db_ids[i]
                sqls = contents
                processed_sqls = []
                for sql in sqls:
                    sql = " ".join(sql.replace("\n", " ").split())
                    sql = process_duplication(sql)
                    if sql.startswith("SELECT"):
                        pass
                    elif sql.startswith(" "):
                        sql = "SELECT" + sql
                    else:
                        sql = "SELECT " + sql
                    processed_sqls.append(sql)
                result = {
                    'db_id': db_id,
                    'p_sqls': processed_sqls
                }
                final_sqls = await get_sqls([result], self.conf.self_consistent_set_size,
                                            self.conf.run_conf.dataset_config.get_db_path())
                results.extend(final_sqls)
        return results

    async def ask_file(self, in_path: str, out_path: str):
        print(f"Asking GPT {in_path} ==> {out_path}")
        if os.path.exists(out_path) and not self.conf.force:
            log(f"Output path exists: {out_path}, skip asking gpt.")
            return
        await self.gpt_asker.ask_file(in_path, out_path)
