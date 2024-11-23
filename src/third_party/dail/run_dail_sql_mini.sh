set -eu

echo "data_preprocess"
#python data_preprocess.py

echo "generate question with EUCDISQUESTIONMASK"
python3.11 generate_question.py \
--data_type spider \
--split test \
--tokenizer gpt-3.5-turbo \
--max_seq_len 4096 \
--prompt_repr SQL \
--k_shot 9 \
--example_type QA \
--selector_type  EUCDISQUESTIONMASK

echo "generate SQL by GPT-4 for EUCDISMASKPRESKLSIMTHR as the pre-generated SQL query"
python3.11 ask_llm.py \
--openai_api_key "$TOKEN"  \
--openai_group_id org-uepjYjYK5sZA3J2gTh6bBlRU \
--model gpt-4 \
--question ./dataset/process/SPIDER-TEST_SQL_9-SHOT_EUCDISQUESTIONMASK_QA-EXAMPLE_CTX-200_ANS-4096/ \
--end_index 2

echo "generate question with EUCDISMASKPRESKLSIMTHR"
python3.11 generate_question.py \
--data_type spider \
--split test \
--tokenizer gpt-3.5-turbo \
--max_seq_len 4096 \
--selector_type EUCDISMASKPRESKLSIMTHR \
--pre_test_result ./results/DAIL-SQL+GPT-4.txt \
--prompt_repr SQL \
--k_shot 9 \
--example_type QA

echo "generate SQL by GPT-4 for EUCDISMASKPRESKLSIMTHR"
python3.11 ask_llm.py \
--openai_api_key $TOKEN  \
--openai_group_id org-uepjYjYK5sZA3J2gTh6bBlRU \
--model gpt-4 \
--question ./dataset/process/SPIDER-TEST_SQL_9-SHOT_EUCDISMASKPRESKLSIMTHR_QA-EXAMPLE_CTX-200_ANS-4096/ \
--end_index 2

