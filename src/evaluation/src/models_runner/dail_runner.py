import json
import math
import os.path

from src.evaluation.src.models_runner.runner import ModelRunner, execute_command


DAIL_FILE = 'src/models/dail/ask_llm.py'
GEN_FILE = 'src/models/dail/generate_question.py'


class DailRunner(ModelRunner):

    def preprocess(self):

        selector_type = 'EUCDISQUESTIONMASK'

        # command = "python3 --version"

        command = (f"python3 {GEN_FILE}  \
        --data_type sqlyzr \
        --split test \
        --tokenizer gpt-3.5-turbo \
        --max_seq_len 4096 \
        --prompt_repr SQL \
        --k_shot 9 \
        --example_type QA \
        --selector_type {selector_type} "
                   f"--dataset_dir {self.dataset_dir} "
                   f"--output_dir {self.dataset_dir}")

        execute_command(command)

    def get_total_number_of_questions(self):
        with open(f"{self.dataset_dir}/dev.json", 'r') as f:
            data = json.load(f)
            return len(data)

    def run_model_single_time(self, k):

        # self.preprocess()
        total_questions = self.get_total_number_of_questions()
        step =  math.ceil(total_questions / self.thread_count)
        start_idx = step * k
        end_idx = min(start_idx + step, total_questions)
        k_output_path = f"{self.output_dir}_{k}"
        database_dir = os.path.join(self.dataset_dir, "database")
        question_file = os.path.join(self.dataset_dir)
        # temp = 1
        model = 'gpt-4'
        token = "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"
        group_id = "org-uepjYjYK5sZA3J2gTh6bBlRU"
        DAIL_command = (f"python3 {DAIL_FILE} --db_dir {database_dir} \
                        --question {question_file} --output {k_output_path} \
                        --temperature {self.temp} --openai_api_key {token} \
                        --openai_group_id {group_id} --model {model} "
                        f"--start_index {start_idx} --end_index {end_idx}")
        execute_command(DAIL_command)



def main():
    runner = DailRunner("data/dataset/data", f"data/dataset/output_results/dail/{1.0}_{1}_out", 4, 1.0)
    # runner.preprocess()
    runner.run()
    runner.merge_results()


if __name__ == '__main__':
    main()
