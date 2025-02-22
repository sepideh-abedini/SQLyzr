from dataclasses import dataclass
import pandas as pd

from src.third_party.din.spider.classification_prompt import CLASSIFICATION_PROMPT
from src.third_party.din.spider.easy_prompt import EASY_PROMPT
from src.third_party.din.spider.hard_prompt import HARD_PROMPT
from src.third_party.din.spider.medium_prompt import MEDIUM_PROMPT
from src.third_party.din.spider.schema_linking_prompt import SCHEMA_LINKING_PROMPT


@dataclass
class PromptMaker:
    spider_foreign: pd.DataFrame
    spider_schema: pd.DataFrame
    spider_primary: pd.DataFrame

    def __init__(self, tables_path):
        schema_df = pd.read_json(tables_path)
        schema_df = schema_df.drop(['column_names', 'table_names'], axis=1)
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
                if type(primary_key) is list:
                    for sub_primary_key in primary_key:
                        index, column = col_names[sub_primary_key]
                        p_keys.append([row['db_id'], tables[index], column])
                else:
                    index, column = col_names[primary_key]
                    p_keys.append([row['db_id'], tables[index], column])
            for foreign_key in foreign_keys:
                first, second = foreign_key
                first_index, first_column = col_names[first]
                second_index, second_column = col_names[second]
                f_keys.append([row['db_id'], tables[first_index], tables[second_index], first_column, second_column])
        self.spider_schema = pd.DataFrame(schema, columns=['Database name', ' Table Name', ' Field Name', ' Type'])
        self.spider_primary = pd.DataFrame(p_keys, columns=['Database name', 'Table Name', 'Primary Key'])
        self.spider_foreign = pd.DataFrame(f_keys, columns=['Database name', 'First Table Name', 'Second Table Name',
                                                            'First Table Foreign Key',
                                                            'Second Table Foreign Key'])

    def hard_prompt_maker(self, test_sample_text, database, schema_links, sub_questions):
        instruction = "# Use the intermediate representation and the schema links to generate the SQL queries for each of the questions.\n"
        fields = self.find_fields_MYSQL_like("college_2")
        fields += "Foreign_keys = " + self.find_foreign_keys_MYSQL_like("college_2") + '\n'
        fields += self.find_fields_MYSQL_like(database)
        fields += "Foreign_keys = " + self.find_foreign_keys_MYSQL_like(database) + '\n'
        stepping = f'''\nA: Let's think step by step. "{test_sample_text}" can be solved by knowing the answer to the following sub-question "{sub_questions}".'''
        fields += "\n"
        prompt = instruction + fields + HARD_PROMPT + 'Q: "' + test_sample_text + '"' + '\nschema_links: ' + schema_links + stepping + '\nThe SQL query for the sub-question"'
        return prompt

    def medium_prompt_maker(self, test_sample_text, database, schema_links):
        instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
        fields = self.find_fields_MYSQL_like("college_2")
        fields += "Foreign_keys = " + self.find_foreign_keys_MYSQL_like("college_2") + '\n'
        fields += self.find_fields_MYSQL_like(database)
        fields += "Foreign_keys = " + self.find_foreign_keys_MYSQL_like(database) + '\n'
        fields += "\n"
        prompt = instruction + fields + MEDIUM_PROMPT + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nA: Let’s think step by step.'
        return prompt

    def easy_prompt_maker(self, test_sample_text, database, schema_links):
        instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
        fields = self.find_fields_MYSQL_like("college_2")
        fields += self.find_fields_MYSQL_like(database)
        fields += "\n"
        prompt = instruction + fields + EASY_PROMPT + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nSQL:'
        return prompt

    def classification_prompt_maker(self, test_sample_text, database, schema_links):
        instruction = "# For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN.\n"
        instruction += "\nif need nested queries: predict NESTED\n"
        instruction += "elif need JOIN and don't need nested queries: predict NON-NESTED\n"
        instruction += "elif don't need JOIN and don't need nested queries: predict EASY\n\n"
        fields = self.find_fields_MYSQL_like("college_2")
        fields += "Foreign_keys = " + self.find_foreign_keys_MYSQL_like("college_2") + '\n'
        fields += self.find_fields_MYSQL_like(database)
        fields += "Foreign_keys = " + self.find_foreign_keys_MYSQL_like(database) + '\n'
        fields += "\n"
        prompt = instruction + fields + CLASSIFICATION_PROMPT + 'Q: "' + test_sample_text + '\nschema_links: ' + schema_links + '\nA: Let’s think step by step.'
        return prompt

    def schema_linking_prompt_maker(self, test_sample_text, database):
        instruction = "# Find the schema_links for generating SQL queries for each question based on the database schema and Foreign keys.\n"
        fields = self.find_fields_MYSQL_like(database)
        foreign_keys = "Foreign_keys = " + self.find_foreign_keys_MYSQL_like(database) + '\n'
        prompt = instruction + SCHEMA_LINKING_PROMPT + fields + foreign_keys + 'Q: "' + test_sample_text + """"\nA: Let’s think step by step."""
        return prompt

    def find_foreign_keys_MYSQL_like(self, db_name):
        df = self.spider_foreign[self.spider_foreign['Database name'] == db_name]
        output = "["
        for index, row in df.iterrows():
            output += row['First Table Name'] + '.' + row['First Table Foreign Key'] + " = " + row[
                'Second Table Name'] + '.' + row['Second Table Foreign Key'] + ','
        output = output[:-1] + "]"
        return output

    def find_fields_MYSQL_like(self, db_name):
        df = self.spider_schema[self.spider_schema['Database name'] == db_name]
        df = df.groupby(' Table Name')
        output = ""
        for name, group in df:
            output += "Table " + name + ', columns = ['
            for index, row in group.iterrows():
                output += row[" Field Name"] + ','
            output = output[:-1]
            output += "]\n"
        return output

    def find_primary_keys_MYSQL_like(self, db_name):
        df = self.spider_primary[self.spider_primary['Database name'] == db_name]
        output = "["
        for index, row in df.iterrows():
            output += row['Table Name'] + '.' + row['Primary Key'] + ','
        output = output[:-1]
        output += "]\n"
        return output

    def debuger(self, test_sample_text, database, sql):
        instruction = """#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is.
    #### Use the following instructions for fixing the SQL QUERY:
    1) Use the database values that are explicitly mentioned in the question.
    2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
    3) Use DESC and DISTINCT when needed.
    4) Pay attention to the columns that are used for the GROUP BY statement.
    5) Pay attention to the columns that are used for the SELECT statement.
    6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
    7) Use GROUP BY on one column only.

    """
        fields = self.find_fields_MYSQL_like(database)
        fields += "Foreign_keys = " + self.find_foreign_keys_MYSQL_like(database) + '\n'
        fields += "Primary_keys = " + self.find_primary_keys_MYSQL_like(database)
        prompt = instruction + fields + '#### Question: ' + test_sample_text + '\n#### SQLite SQL QUERY\n' + sql + '\n#### SQLite FIXED SQL QUERY\nSELECT'
        return prompt
