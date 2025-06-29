import os
import re
from typing import List

from src.gpt.models import BatchInputRequest
from src.pred.predictor import Predictor, process_responses
from src.pred.process_tables import get_dbs
from src.pred.simple_prompt import SIMPLE_PREDICTOR_PROMPT


class SimplePredictor(Predictor):
    llm_params = {
        'model': os.environ.get("SQLYZR_LLM_MODEL", "gpt-4.1"),
        'max_completion_tokens': 600
    }

    tables_data = dict()

    async def _run_internal(self):
        print("SIMPLE PREDICTOR STARTED!")
        print(self.llm_params)
        conf = self._run_conf

        self.dbs = get_dbs(self._run_conf.dataset_config.get_tables_path())

        in_file = f"{conf.get_pred_path()}.in.jsonl"
        out_file = f"{conf.get_pred_path()}.out.jsonl"

        self._gen_batch_file(in_file, self.__generate_schema_req)

        await self._ask_file(in_file, out_file)

        sqls = process_responses(out_file, self._process_llm_response)

        self._save_sqls(sqls)

    def _process_llm_response(self, i: int, content: str) -> str:
        match = re.search(r".*```(?:\w+)?\s*(.*?)```.*", content, re.DOTALL)
        if match:
            content = match.group(1).strip() if match else ""
        return content

    def _get_prompt(self, db_id, question):
        schema = self.dbs[db_id].to_yaml()
        return SIMPLE_PREDICTOR_PROMPT.format(question=question, schema=schema)

    def __generate_schema_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        prompt = self._get_prompt(db_id, question)
        idx = f"simple_{self._run_conf.dataset_config.dataset_type}_{i}"
        return self._create_batch_req(idx, prompt, self.llm_params)

    def get_out_batch_files(self) -> List[str]:
        return ["out.jsonl"]
