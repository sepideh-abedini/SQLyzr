import json
from sql_parser import SqlParser

class InputParser:
    def __init__(self) -> None:
        self.parser = SqlParser()
    
    def load_json(self, path):
        with open("../models/spider/dev.json") as f:
            j = json.load(f)
        self.data = j
    
    def sample(self, count):
        self.data = self.data[:min(count, len(self.data)) - 1]
    
    def get_list(self, key):
        return [e[key] for e in self.data]
    
    def get_statements(self):
        queries = self.get_list('query')
        statements = []
        for idx, query_str in enumerate(queries):
            try:
                statement = self.parser.to_statement(query_str)
                statements.append(statement)
            except:
                print("Failed to process {}th query".format(idx))
                print("Query: {}".format(query_str))
                raise
        print("Successfully processed {}/{} queries".format(len(statements), len(queries)))
        return statements


    