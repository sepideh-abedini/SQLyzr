from src.models_runner.runner import ModelRunner, execute_command


DAIL_FILE = 'models/dail/ask_llm.py'
GEN_FILE = 'models/dail/generate_question.py'


class DailRunner(ModelRunner):

    def preprocess(self):

        selector_type = 'EUCDISQUESTIONMASK'

        # command = "python3 --version"

        command = (f"python3 {GEN_FILE}  \
        --data_type spider \
        --split test \
        --tokenizer gpt-3.5-turbo \
        --max_seq_len 4096 \
        --prompt_repr SQL \
        --k_shot 9 \
        --example_type QA \
        --selector_type {selector_type}")

        execute_command(command)

    def run(self, dataset_dir, output_dir):

        # self.preprocess()
        question_file = "models/dail/dataset/process/SPIDER-TEST_SQL_9-SHOT_EUCDISMASKPRESKLSIMTHR_QA-EXAMPLE_CTX-200_ANS-4096"
        temp = 1
        model = 'gpt-4'
        end_index = 20
        token = "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"
        group_id = "org-uepjYjYK5sZA3J2gTh6bBlRU"
        DAIL_command = (f"python3 {DAIL_FILE} --db_dir {dataset_dir} \
                        --question {question_file} --output {output_dir} \
                        --temperature {temp} --openai_api_key {token} \
                        --openai_group_id {group_id} --model {model} --end_index {end_index}")
        execute_command(DAIL_command)

def main():
    runner = DailRunner()
    runner.run("models/dail/dataset/spider/database", "dataset/output_results/dail")


if __name__ == '__main__':
    main()
