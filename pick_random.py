import asyncio
import os
import random

from openai import AsyncClient
import tqdm

from src.util.file_utils import read_json, write_json
from src.util.schema_repo import DatabaseSchemaRepo

PROMPT = """
I give you a NL question, its corresponding SQL query and the schema of the underlying database.
Give me the schema linking. 
Schema linking is a mapping between the n-grams in the question and table and column names.
Example:
NL: "What is the name of the instructor who is in Statistics department and earns the lowest salary?"
SQL: "SELECT name FROM instructor WHERE dept_name  =  'Statistics' ORDER BY salary LIMIT 1"
Schema: "\nTables: \n\tTable Name: classroom\n\t\tColumns:\n\t\t\tColumn Name: building, Column type: text\n\t\t\tColumn Name: room_number, Column type: text\n\t\t\tColumn Name: capacity, Column type: number\n\tTable Name: department\n\t\tColumns:\n\t\t\tColumn Name: dept_name, Column type: text\n\t\t\tColumn Name: building, Column type: text\n\t\t\tColumn Name: budget, Column type: number\n\tTable Name: course\n\t\tColumns:\n\t\t\tColumn Name: course_id, Column type: text\n\t\t\tColumn Name: title, Column type: text\n\t\t\tColumn Name: dept_name, Column type: text\n\t\t\tColumn Name: credits, Column type: number\n\tTable Name: instructor\n\t\tColumns:\n\t\t\tColumn Name: id, Column type: text\n\t\t\tColumn Name: name, Column type: text\n\t\t\tColumn Name: dept_name, Column type: text\n\t\t\tColumn Name: salary, Column type: number\n\tTable Name: section\n\t\tColumns:\n\t\t\tColumn Name: course_id, Column type: text\n\t\t\tColumn Name: sec_id, Column type: text\n\t\t\tColumn Name: semester, Column type: text\n\t\t\tColumn Name: year, Column type: number\n\t\t\tColumn Name: building, Column type: text\n\t\t\tColumn Name: room_number, Column type: text\n\t\t\tColumn Name: time_slot_id, Column type: text\n\tTable Name: teaches\n\t\tColumns:\n\t\t\tColumn Name: id, Column type: text\n\t\t\tColumn Name: course_id, Column type: text\n\t\t\tColumn Name: sec_id, Column type: text\n\t\t\tColumn Name: semester, Column type: text\n\t\t\tColumn Name: year, Column type: number\n\tTable Name: student\n\t\tColumns:\n\t\t\tColumn Name: id, Column type: text\n\t\t\tColumn Name: name, Column type: text\n\t\t\tColumn Name: dept_name, Column type: text\n\t\t\tColumn Name: tot_cred, Column type: number\n\tTable Name: takes\n\t\tColumns:\n\t\t\tColumn Name: id, Column type: text\n\t\t\tColumn Name: course_id, Column type: text\n\t\t\tColumn Name: sec_id, Column type: text\n\t\t\tColumn Name: semester, Column type: text\n\t\t\tColumn Name: year, Column type: number\n\t\t\tColumn Name: grade, Column type: text\n\tTable Name: advisor\n\t\tColumns:\n\t\t\tColumn Name: s_id, Column type: text\n\t\t\tColumn Name: i_id, Column type: text\n\tTable Name: time_slot\n\t\tColumns:\n\t\t\tColumn Name: time_slot_id, Column type: text\n\t\t\tColumn Name: day, Column type: text\n\t\t\tColumn Name: start_hr, Column type: number\n\t\t\tColumn Name: start_min, Column type: number\n\t\t\tColumn Name: end_hr, Column type: number\n\t\t\tColumn Name: end_min, Column type: number\n\tTable Name: prereq\n\t\tColumns:\n\t\t\tColumn Name: course_id, Column type: text\n\t\t\tColumn Name: prereq_id, Column type: text\n"
Schema Link: [ "name: C#instructor.name", "instructor = T#instructor, "department = T#department",  "salary = T#instructor.salary" ] 
Now, find the schema linking as the given format for the following NL question, SQL query and DB schema:
NL: {}
SQL: {}
Schema: {}
"""


def sample_random_data(path):
    data = read_json(path)
    samples = random.sample(range(0, len(data)), 50)
    rand_picks = []
    schema_repo = DatabaseSchemaRepo("data/spider/tables.json")

    for i in range(len(data)):
        if i in samples:
            rand_sample = data[i]
            schema = str(schema_repo.dbs[rand_sample['db_id']])
            rand_picks.append({
                'id': i,
                'dataset': 'spider',
                'db_id': rand_sample['db_id'],
                'question': rand_sample['question'],
                'SQL': rand_sample['query'],
                'evidence': "",
                "difficulty": "simple",
                "evidence_added": True,
                "question_toks": rand_sample['question_toks'],
                'schema': schema,
            })
    write_json("tmp/rand.json", rand_picks)


async def get_schema_link(entry):
    client = AsyncClient(
        organization=os.getenv("OPENAI_GROUP_ID"),
        project=os.getenv("OPENAI_PROJ_ID"),
        timeout=int(os.getenv("OPENAI_TIMEOUT", 60))
    )
    msg = PROMPT.format(entry['question'], entry['SQL'], entry['schema'])
    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": msg
            }
        ]
    )
    return completion.choices[0].message.content


async def gen():
    data = read_json("tmp/rand.json")
    tables = read_json("data/spider/tables.json")
    result = []
    for entry in tqdm.tqdm(data, total=len(data)):
        schema_link = await get_schema_link(entry)
        entry['schema_link'] = schema_link
        result.append(entry)
    write_json("tmp/rand_with_schema.json", result)


def extract_tables():
    rand_tables = dict()
    data = read_json("tmp/rand.json")
    tables = read_json("data/spider/tables.json")
    db_info = dict()
    for entry in tqdm.tqdm(data, total=len(data)):
        for db in tables:
            if db['db_id'] == entry['db_id']:
                db['column_descriptions'] = db["column_names_original"]
                cs = []
                for c in db['column_descriptions']:
                    c[1] = None
                    cs.append(c)
                db['column_descriptions'] = cs
                db['sample_rows'] = dict()
                db['table_to_projDataset'] = dict()
                for t in db['table_names_original']:
                    db['sample_rows'][t] = []
                    db['table_to_projDataset'][t] = ""
                rand_tables[db['db_id']] = db

                db_info[db['db_id']] = {
                    'db_id': db['db_id'],
                    'count': len(db['column_names_original'])
                }

    write_json("tmp/rand_tables.json", list(rand_tables.values()))
    write_json("tmp/rand_db_info.json", list(db_info.values()))


def update_data():
    data = read_json("tmp/rand_with_schema.json")
    entries = []
    for e in data:
        e['instance_id'] = "i1"
        entries.append(e)
    write_json("tmp/rand_with_schema.v2.json", entries)


def show_data():
    data = read_json("tmp/rand_with_schema.v2.json")
    annotated = []
    for row in data:
        print("NL: ", row['question'])
        print("SQL: ", row['SQL'])
        print("Schema Link: ", row['schema_link'])
        # print("Schema: ", row['schema'])
        print("--------------------------------")
        annotation = input("Enter the annotated schema link: ")
        row['annotation'] = annotation
        annotated.append(row)
    write_json("tmp/annotated.json", annotated)


async def main():
    # sample_random_data("data/spider/data.test.json")
    # await gen()
    # extract_tables()
    # update_data()
    show_data()


# sample_random_data("data/spider/data.test.json")

# await get_schema_link()


if __name__ == '__main__':
    asyncio.run(main())
