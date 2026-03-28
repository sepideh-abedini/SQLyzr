import re

from src.model.custom.custom_predictor_interface import CustomPredictorInterface
from src.model.custom.custom_prompt import CUSTOM_PROMPT


class CustomPredictorImpl(CustomPredictorInterface):
    @property
    def llm_params(self):
        return {
            'model': self._run_conf.options.get("llm", "gpt-4.1"),
            'max_completion_tokens': 600
        }

    def _get_prompt(self, db_id, question):
        schema = self.dbs[db_id].to_yaml()
        return CUSTOM_PROMPT.format(question=question, schema=schema)

    def _process_llm_response(self, i: int, content: str) -> str:
        match = re.search(r".*```(?:\w+)?\s*(.*?)```.*", content, re.DOTALL)
        if match:
            content = match.group(1).strip() if match else ""
        return content
