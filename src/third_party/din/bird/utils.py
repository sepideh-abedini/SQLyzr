import glob
import json
import os
import re
from typing import List, Tuple

import pandas as pd
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

def get_database_schema(DB_URI: str) -> str:
    """Get the database schema from the database URI

    Args:
        DB_URI (str): Database URI

    Returns:
        str: Database schema
    """
    db = SQLDatabase.from_uri("sqlite:///" + DB_URI)
    db._sample_rows_in_table_info = 3
    return db.get_table_info_no_throw()


def extract_schema_links(input_text: str) -> List[str]:
    pattern = r'Schema_links:\s*\[(.*?)\]'
    match = re.search(pattern, input_text)
    if match:
        schema_links_str = match.group(1)
        schema_links = [link.strip() for link in schema_links_str.split(',')]
        return schema_links
    else:
        return []


def extract_label_and_sub_questions(input_text: str) -> Tuple[str, List[str]]:
    label_pattern = r'Label:\s*"(.*?)"'
    sub_questions_pattern = r'sub_questions:\s*\[(.*?)\]'

    label_match = re.search(label_pattern, input_text)
    sub_questions_match = re.search(sub_questions_pattern, input_text)

    label = label_match.group(1) if label_match else None

    sub_questions = []
    if sub_questions_match:
        sub_questions_str = sub_questions_match.group(1)
        sub_questions = [question.strip() for question in sub_questions_str.split(',')]

    return label, sub_questions


def extract_sql_query(input_text):
    sql_pattern = r'SQL:\s*(.*?)$'
    match = re.search(sql_pattern, input_text, re.DOTALL)
    return match.group(1).strip() if match else None


def extract_revised_sql_query(input_text):
    sql_pattern = r'Revised_SQL:\s*(.*?)$'
    match = re.search(sql_pattern, input_text, re.DOTALL)
    return match.group(1).strip() if match else None


def update_json_file(json_filename, index, sql_query, db_id):
    try:
        with open(json_filename, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {}

    data[str(index)] = f"{sql_query}\t----- bird -----\t{db_id}"

    with open(json_filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def table_descriptions_parser(database_dir):
    csv_files = glob.glob(f"{database_dir}/*.csv")
    # Iterate over the CSV files
    db_descriptions = ""
    for file_path in csv_files:
        table_name: str = os.path.basename(file_path).replace(".csv", "")
        db_descriptions += f"Table: {table_name}\n"
        table_df = pd.read_csv(file_path, encoding='latin-1')
        for _, row in table_df.iterrows():
            try:
                if pd.notna(row[2]):
                    col_description = re.sub(r'\s+', ' ', str(row[2]))  # noqa: E501
                    val_description = re.sub(r'\s+', ' ', str(row[4]))
                    if pd.notna(row[4]):
                        db_descriptions += f"Column {row[0]}: column description -> {col_description}, value description -> {val_description}\n"  # noqa: E501
                    else:
                        db_descriptions += f"Column {row[0]}: column description -> {col_description}\n"  # noqa: E501
            except Exception as e:
                print(e)
                db_descriptions += "No column description"
        db_descriptions += "\n"
    return db_descriptions
