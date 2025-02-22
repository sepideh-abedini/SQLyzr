import os
import re
import pandas as pd
import json
import glob

from typing import List, Tuple

from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

from src.third_party.din.prompts.bird.prompts import SYSTEM_SCHEMA_LINKING_TEMPLATE, SYSTEM_CLASSIFICATION_TEMPLATE, \
    HUMAN_SCHEMA_LINKING_TEMPLATE, HUMAN_CLASSIFICATION_TEMPLATE, SYSTEM_EASY_CLASS_TEMPLATE, HUMAN_EASY_CLASS_TEMPLATE, \
    SYSTEM_NON_NESTED_CLASS_TEMPLATE, HUMAN_NON_NESTED_CLASS_TEMPLATE, SYSTEM_NESTED_CLASS_TEMPLATE, \
    HUMAN_NESTED_CLASS_TEMPLATE, SYSTEM_SELF_CORRECTION_PROMPT, HUMAN_SELF_CORRECTION_PROMPT
from src.third_party.din.prompts.bird.utils import table_descriptions_parser, get_database_schema, extract_schema_links, \
    extract_label_and_sub_questions, extract_sql_query, extract_revised_sql_query, update_json_file

CHAT = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=2000)
dev_db_path = "data/bird/database"
dev_df = pd.read_json("data/bird/small/data.json")



start_index = 0

if __name__ == "__main__":
    logs_df = pd.DataFrame(
        columns=["question", "gold_query", "db_id", "final_query", "schema_linking", "classification", "sql_generation",
                 "self_correction"])

    # should be removed in the final version
    # dev_df = dev_df.sample(frac=0.03).reset_index(drop=True)
    # print("Number of questions: ", dev_df.shape[0])

    system_schema_linking_prompt = SystemMessagePromptTemplate.from_template(
        SYSTEM_SCHEMA_LINKING_TEMPLATE)  # noqa: E501
    human_schema_linking_prompt = HumanMessagePromptTemplate.from_template(HUMAN_SCHEMA_LINKING_TEMPLATE)  # noqa: E501
    schema_linking_prompt = ChatPromptTemplate.from_messages(
        [system_schema_linking_prompt, human_schema_linking_prompt])  # noqa: E501
    system_classification_prompt = SystemMessagePromptTemplate.from_template(
        SYSTEM_CLASSIFICATION_TEMPLATE)  # noqa: E501
    human_classification_prompt = HumanMessagePromptTemplate.from_template(HUMAN_CLASSIFICATION_TEMPLATE)  # noqa: E501
    classification_prompt = ChatPromptTemplate.from_messages(
        [system_classification_prompt, human_classification_prompt])  # noqa: E501
    system_easy_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_EASY_CLASS_TEMPLATE)  # noqa: E501
    human_easy_prompt = HumanMessagePromptTemplate.from_template(HUMAN_EASY_CLASS_TEMPLATE)  # noqa: E501
    easy_prompt = ChatPromptTemplate.from_messages([system_easy_prompt, human_easy_prompt])  # noqa: E501
    system_easy_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_EASY_CLASS_TEMPLATE)  # noqa: E501
    human_easy_prompt = HumanMessagePromptTemplate.from_template(HUMAN_EASY_CLASS_TEMPLATE)  # noqa: E501
    easy_prompt = ChatPromptTemplate.from_messages([system_easy_prompt, human_easy_prompt])  # noqa: E501
    system_medium_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_NON_NESTED_CLASS_TEMPLATE)  # noqa: E501
    human_medium_prompt = HumanMessagePromptTemplate.from_template(HUMAN_NON_NESTED_CLASS_TEMPLATE)  # noqa: E501
    medium_prompt = ChatPromptTemplate.from_messages([system_medium_prompt, human_medium_prompt])  # noqa: E501
    system_hard_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_NESTED_CLASS_TEMPLATE)  # noqa: E501
    human_hard_prompt = HumanMessagePromptTemplate.from_template(HUMAN_NESTED_CLASS_TEMPLATE)  # noqa: E501
    hard_prompt = ChatPromptTemplate.from_messages([system_hard_prompt, human_hard_prompt])  # noqa: E501
    system_correction_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_SELF_CORRECTION_PROMPT)  # noqa: E501
    human_correction_prompt = HumanMessagePromptTemplate.from_template(HUMAN_SELF_CORRECTION_PROMPT)  # noqa: E501
    correction_prompt = ChatPromptTemplate.from_messages(
        [system_correction_prompt, human_correction_prompt])  # noqa: E501
    accuracy = 0
    for index, row in dev_df.iterrows():
        if index < start_index:
            continue
        print("Processing row: ", index)
        db_uri = dev_db_path + "/" + row["db_id"] + "/" + row["db_id"] + ".sqlite"
        db_descriptions = dev_db_path + "/" + row["db_id"] + "/" + "database_description"  # noqa: E501
        print("Database: ", db_uri)
        columns_descriptions = table_descriptions_parser(db_descriptions)
        schema = get_database_schema(db_uri)
        question = row["question"]
        print("Question: ", question)
        hint = str(row["evidence"])
        question_id = row["question_id"]
        chain = LLMChain(llm=CHAT, prompt=schema_linking_prompt)
        schema_linking = chain.run(question=question, schema=schema, hint=hint,
                                   columns_descriptions=columns_descriptions)  # noqa: E501
        schema_links = extract_schema_links(schema_linking)
        chain = LLMChain(llm=CHAT, prompt=classification_prompt)
        classification = chain.run(
            question=question,
            schema=schema,
            hint=hint,
            columns_descriptions=columns_descriptions,
            schema_links=schema_links)
        label, sub_questions = extract_label_and_sub_questions(classification)
        print("Label: ", label)
        sql_generation = None
        if "EASY" in label:
            chain = LLMChain(llm=CHAT, prompt=easy_prompt)
            easy = chain.run(
                question=question,
                schema=schema,
                hint=hint,
                columns_descriptions=columns_descriptions,
                schema_links=schema_links)
            sql_query = extract_sql_query(easy)
            sql_generation = easy
        elif "NON-NESTED" in label:
            chain = LLMChain(llm=CHAT, prompt=medium_prompt)
            medium = chain.run(
                question=question,
                schema=schema,
                hint=hint,
                columns_descriptions=columns_descriptions,
                schema_links=schema_links)
            sql_query = extract_sql_query(medium)
            sql_generation = medium
        else:
            chain = LLMChain(llm=CHAT, prompt=hard_prompt)
            hard = chain.run(
                question=question,
                schema=schema,
                hint=hint,
                columns_descriptions=columns_descriptions,
                schema_links=schema_links,
                sub_questions=sub_questions)
            sql_query = extract_sql_query(hard)
            sql_generation = hard
        chain = LLMChain(llm=CHAT, prompt=correction_prompt)
        correction = chain.run(
            question=question,
            schema=schema,
            columns_descriptions=columns_descriptions,
            hint=hint,
            sql_query=sql_query)
        finall_sql = extract_revised_sql_query(correction)
        if finall_sql is not None:
            one_liner_sql_query = finall_sql.replace('\n', '').replace('\r', '')
        else:
            if sql_query is not None:
                one_liner_sql_query = sql_query.replace('\n', '').replace('\r', '')
            else:
                one_liner_sql_query = "SELECT * FROM table"  # no query generated, placeholder to avoid errors # noqa: E501
        new_row_df = pd.DataFrame(
            [[question, row["SQL"], row["db_id"], one_liner_sql_query, schema_linking, classification, sql_generation,
              correction]],  # noqa: E501
            columns=["question", "gold_query", "db_id", "final_query", "schema_linking", "classification",
                     "sql_generation", "self_correction"])
        logs_df = pd.concat([logs_df, new_row_df], ignore_index=True)
        logs_df.to_csv("logs.csv", index=False)
        update_json_file("predict_dev.json", index, one_liner_sql_query, row["db_id"])
        print("final sql query: ", one_liner_sql_query)
        print("Gold sql query: ", row["SQL"])
        print("--------------------------------------------------")
