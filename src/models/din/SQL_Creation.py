import random

import pandas as pd
import time
import openai
import os
import sys
import json

GPT_MODEL = "gpt-4o-mini"
             # "gpt-3.5-turbo"
#"gpt-4"
# GPT_MODEL = "gpt-4o-mini"

#----------------------------------------------------prompts-----------------------------------------------

tag_definitions = '''
Tag Definitions:
SelectType.SingleColumn: Only a single column in the select clause
SelectType.MultipleColumn: Multiple columns in the select clause
ExtraKeywords.OrderBy: Having orderby clause
'''
#----------------------------------------------------------------------------------------------------------

# API_KEY = "sk-proj-xRpA0aLQLIQQgWd0G8MZT3BlbkFJdLrCzayOcBtrLQ6NMokC"
API_KEY = "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"
# API_KEY = "YOUR_API_KEY"

os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")


def load_data(DATASET):
    return pd.read_json(DATASET)

def hard_prompt_maker(database, tags):
  instruction = ("# Use the following information about the tables in a database and definitions of the tags, "
                 "generate a SQL that matches the given tags.\n")
  fields = find_fields_MYSQL_like("college_2")
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "\n"
  tags_spec = f'''
    Now, generate an SQL query that matches the following tags:
    {tags}
  '''
  prompt = instruction + fields + tag_definitions + tags_spec +'"' + '\n'
  return prompt

def find_foreign_keys_MYSQL_like(db_name):
  df = spider_foreign[spider_foreign['Database name'] == db_name]
  output = "["
  for index, row in df.iterrows():
    output += row['First Table Name'] + '.' + row['First Table Foreign Key'] + " = " + row['Second Table Name'] + '.' + row['Second Table Foreign Key'] + ','
  output= output[:-1] + "]"
  return output

def find_fields_MYSQL_like(db_name):
  df = spider_schema[spider_schema['Database name'] == db_name]
  df = df.groupby(' Table Name')
  output = ""
  for name, group in df:
    output += "Table " +name+ ', columns = ['
    for index, row in group.iterrows():
      output += row[" Field Name"]+','
    output = output[:-1]
    output += "]\n"
  return output
def find_primary_keys_MYSQL_like(db_name):
  df = spider_primary[spider_primary['Database name'] == db_name]
  output = "["
  for index, row in df.iterrows():
    output += row['Table Name'] + '.' + row['Primary Key'] +','
  output = output[:-1]
  output += "]\n"
  return output
def creatiing_schema(DATASET_JSON):
    schema_df = pd.read_json(DATASET_JSON)
    schema_df = schema_df.drop(['column_names','table_names'], axis=1)
    schema = []
    f_keys = []
    p_keys = []
    for index, row in schema_df.iterrows():
        tables = row['table_names_original']
        col_names = row['column_names_original']
        col_types = row['column_types']
        foreign_keys = row['foreign_keys']
        primary_keys = row['primary_keys']
        for col, col_type in zip(col_names, col_types):
            index, col_name = col
            if index == -1:
                for table in tables:
                    schema.append([row['db_id'], table, '*', 'text'])
            else:
                schema.append([row['db_id'], tables[index], col_name, col_type])
        for primary_key in primary_keys:
            print(row['db_id'])
            index, column = col_names[primary_key]
            p_keys.append([row['db_id'], tables[index], column])
        for foreign_key in foreign_keys:
            first, second = foreign_key
            first_index, first_column = col_names[first]
            second_index, second_column = col_names[second]
            f_keys.append([row['db_id'], tables[first_index], tables[second_index], first_column, second_column])
    spider_schema = pd.DataFrame(schema, columns=['Database name', ' Table Name', ' Field Name', ' Type'])
    spider_primary = pd.DataFrame(p_keys, columns=['Database name', 'Table Name', 'Primary Key'])
    spider_foreign = pd.DataFrame(f_keys,
                        columns=['Database name', 'First Table Name', 'Second Table Name', 'First Table Foreign Key',
                                 'Second Table Foreign Key'])
    return spider_schema,spider_primary,spider_foreign

def GPT4_generation(prompt):
  print("###################################### Prompt ########################")
  print(prompt)
  print("###################################### Prompt ########################")
  response = openai.chat.completions.create(
    model=GPT_MODEL,
    messages=[{"role": "user", "content": prompt}],
    n = 1,
    stream = False,
    temperature=0,
    max_tokens=600,
    # top_p = 1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop = ["Q:"]
  )
  tokens = response.usage.total_tokens
  # print("Total token usage: ", tokens)
  return response.choices[0].message.content, tokens

def DB_selection(category:str):
    result = []
    dict = {}
    path = TABLES_PATH
    with open(path, 'r') as f:
        tables = json.load(f)
        result = list(map(lambda x: (x['db_id'], len(x['table_names'])), tables))
        sort = sorted(result, key=lambda x: x[1], reverse=True)

        dict = {'c6' : 17, 'c5': 16, 'c4':10, 'c3':7, 'c2': 4, 'c1': 2}

        num = dict[category]

        final_result = list(filter(lambda x: x[1] >= num, sort))
        random.shuffle(final_result)
        return final_result[0][0]

def SQL_from_cat(category:str):
    # val_df = load_data(DATASET)
    CODEX = []
    total_cost = 0
    # for index, row in val_df.iterrows():
    db_id = DB_selection(category)

    SQL, tokens = GPT4_generation(
        hard_prompt_maker(db_id, "SelectType.SingleColumn, ExtraKeywords.OrderBy"))
    total_cost += tokens

    return SQL









TABLES_PATH = "../spider/tables.json"

# START = 180
if __name__ == '__main__':

    spider_schema, spider_primary, spider_foreign = creatiing_schema(TABLES_PATH)


    cat = sys.argv[1]
    print(SQL_from_cat(cat))


    # CODEX.append([row['question'], SQL, row['query'], row['db_id']])
    # df = pd.DataFrame(CODEX, columns=['NLQ', 'PREDICTED SQL', 'GOLD SQL', 'DATABASE'])

    # 17<= C6 <=65
    #  16<= c5
    #  10<= c4
    # 7 <= c3
    # 4 <= c2


