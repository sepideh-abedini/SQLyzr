import re
from abc import abstractmethod
from typing import List

from src.gpt.models import BatchInputRequest
from loguru import logger

from src.model.predictor import Predictor, process_responses
from src.model.process_tables import get_dbs


class CustomPredictorInterface(Predictor):
    @property
    @abstractmethod
    def llm_params(self):
        pass

    tables_data = dict()

    async def _run_internal(self):
        logger.info("CUSTOM PREDICTOR STARTED!")
        logger.info("LLM PARAMS:")
        logger.info(self.llm_params)
        logger.info(f"USING LLM: {self.llm_params}")
        conf = self._run_conf

        self.dbs = get_dbs(self._run_conf.dataset_config.get_tables_path())

        in_file = f"{conf.get_pred_path()}.in.jsonl"
        out_file = f"{conf.get_pred_path()}.out.jsonl"

        self._gen_batch_file(in_file, self.__generate_req)

        await self._ask_file(in_file, out_file)

        sqls = process_responses(out_file, self._process_llm_response)

        self._save_sqls(sqls)

    def __generate_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        prompt = self._get_prompt(db_id, question)
        idx = f"simple_{self._run_conf.dataset_config.dataset_type}_{i}"
        return self._create_batch_req(idx, prompt, self.llm_params)

    def get_out_batch_files(self) -> List[str]:
        return ["out.jsonl"]

    @abstractmethod
    def _get_prompt(self, db_id, question):
        pass

    @abstractmethod
    def _process_llm_response(self, i: int, content: str) -> str:
        pass
