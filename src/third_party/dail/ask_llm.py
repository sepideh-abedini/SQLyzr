import argparse
import json
import os

from torch.utils.data import DataLoader
from tqdm import tqdm

from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.llm.chatgpt import init_chatgpt, ask_llm
from src.third_party.dail.utils.enums import LLM
from src.third_party.dail.utils.post_process import process_duplication, get_sqls

MODEL = LLM.GPT_35_TURBO
BATCH_SIZE = 1
SELF_CONSISTENT_SET_SIZE = 5


def run_dail(conf: DailConfig):
    start_index = 0
    end_index = 100_000
    questions_json = json.load(open(conf.questions_path(), "r"))
    questions = [_["prompt"] for _ in questions_json["questions"]]
    db_ids = [_["db_id"] for _ in questions_json["questions"]]

    # init openai api
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_group_id = os.getenv("OPENAI_GROUP_ID")
    init_chatgpt(openai_api_key, openai_group_id, MODEL)

    question_loader = DataLoader(questions, batch_size=BATCH_SIZE, shuffle=False, drop_last=False)

    token_cnt = 0
    with open(conf.run_conf.get_pred_path(), "w") as f:
        for i, batch in enumerate(question_loader):
            if i < start_index:
                continue
            if i >= end_index:
                break
            try:
                res = ask_llm(MODEL, batch, conf.run_conf.temp, SELF_CONSISTENT_SET_SIZE)
            except Exception as e:
                print(f"The {i}-th question has too much tokens! Return \"SELECT\" instead")
                print(e)
                res = ""

            # parse result
            token_cnt += res["total_tokens"]
            if SELF_CONSISTENT_SET_SIZE == 1:
                for sql in res["response"]:
                    # remove \n and extra spaces
                    sql = " ".join(sql.replace("\n", " ").split())
                    sql = process_duplication(sql)
                    # python version should >= 3.8
                    if sql.startswith("SELECT"):
                        f.write(sql + "\n")
                    elif sql.startswith(" "):
                        f.write("SELECT" + sql + "\n")
                    else:
                        f.write("SELECT " + sql + "\n")
            else:
                results = []
                cur_db_ids = db_ids[i * BATCH_SIZE: i * BATCH_SIZE + len(batch)]
                for sqls, db_id in zip(res["response"], cur_db_ids):
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
                    final_sqls = get_sqls([result], SELF_CONSISTENT_SET_SIZE,
                                          conf.run_conf.dataset_config.get_db_path())

                    for sql in final_sqls:
                        f.write(sql + "\n")
        f.write(f"tokens:{token_cnt}")
