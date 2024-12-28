import json

from nltk.tokenize import NLTKWordTokenizer

from src.augmentation.spider.paser_sql import get_schemas_from_json, Schema
from src.augmentation.spider.process_sql import tokenize, get_sql


def main():
    data = json.load(open("data/aug/gpt.json"))
    table_file = "data/spider/tables.json"
    nl_tokenizer = NLTKWordTokenizer()

    output = []
    for row in data:
        db_id = row['db_id']
        schemas, db_names, tables = get_schemas_from_json(table_file)
        schema = schemas[db_id]
        table = tables[db_id]
        schema = Schema(schema, table)
        sql = row['query'].replace("\n", " ")
        nl = row['question']
        sql_toks = tokenize(sql)
        nl_toks = nl_tokenizer.tokenize(nl)
        row['query'] = sql
        row['query_toks'] = sql_toks
        row['question_toks'] = nl_toks
        try:
            sql_label = get_sql(schema, sql)
        except Exception as e:
            print("Failed to parse sql:")
            print(e)
            print(sql)
            print("----------------------------")
            continue
        row['sql'] = sql_label
        output.append(row)

    out_file = open("data/aug/gpt.post.json", "w")
    out_file.write(json.dumps(output, indent=4))
    print(f"Input: {len(data)}")
    print(f"Output: {len(output)}")


if __name__ == '__main__':
    main()
