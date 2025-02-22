import os
import re
import pandas as pd
import json
import glob

from typing import List, Tuple
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from src.third_party.din.bird.prompts import *
from src.third_party.din.bird.utils import extract_schema_links, extract_label_and_sub_questions, extract_sql_query, \
    extract_revised_sql_query, table_descriptions_parser, get_database_schema

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


def get_db_info(db_uri, db_description_dir):
    # db_uri = dev_db_path + "/" + row["db_id"] + "/" + row["db_id"] + ".sqlite"
    # db_descriptions = dev_db_path + "/" + row["db_id"] + "/" + "database_description"  # noqa: E501
    columns_descriptions = table_descriptions_parser(db_description_dir)
    schema = get_database_schema(db_uri)
    return schema, columns_descriptions


def send_prompt(msg):
    return ""


def run(schema, columns_descriptions, question, hint):
    msg = schema_linking_prompt.format(question=question, schema=schema, hint=hint,
                                       columns_descriptions=columns_descriptions)
    schema_linking = send_prompt(msg)
    schema_links = extract_schema_links(schema_linking)

    msg = classification_prompt.format(question=question,
                                       schema=schema,
                                       hint=hint,
                                       columns_descriptions=columns_descriptions,
                                       schema_links=schema_links)
    classification = send_prompt(msg)
    label, sub_questions = extract_label_and_sub_questions(classification)

    if "EASY" in label:
        msg = easy_prompt.run(
            question=question,
            schema=schema,
            hint=hint,
            columns_descriptions=columns_descriptions,
            schema_links=schema_links)
        easy = send_prompt(msg)
        sql_query = extract_sql_query(easy)
    elif "NON-NESTED" in label:
        msg = medium_prompt.format(question=question,
                                   schema=schema,
                                   hint=hint,
                                   columns_descriptions=columns_descriptions,
                                   schema_links=schema_links)
        medium = send_prompt(msg)
        sql_query = extract_sql_query(medium)
    else:
        msg = hard_prompt.format(
            question=question,
            schema=schema,
            hint=hint,
            columns_descriptions=columns_descriptions,
            schema_links=schema_links,
            sub_questions=sub_questions)
        hard = send_prompt(msg)
        sql_query = extract_sql_query(hard)

    msg = correction_prompt.format(question=question,
                                   schema=schema,
                                   columns_descriptions=columns_descriptions,
                                   hint=hint,
                                   sql_query=sql_query)
    correction = send_prompt(msg)
    finall_sql = extract_revised_sql_query(correction)

    if finall_sql is not None:
        one_liner_sql_query = finall_sql.replace('\n', '').replace('\r', '')
    else:
        if sql_query is not None:
            one_liner_sql_query = sql_query.replace('\n', '').replace('\r', '')
        else:
            one_liner_sql_query = "SELECT * FROM table"  # no query generated, placeholder to avoid errors # noqa: E501
    return one_liner_sql_query
