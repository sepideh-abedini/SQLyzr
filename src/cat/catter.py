from src.cat.categorizer import Categorizer
from src.cat.tag_extractor import TagExtractor
from src.parse.parser import SqlParser


class Catter:
    def __init__(self):
        self.parser = SqlParser()
        self.tag_extractor = TagExtractor()
        self.categorizer = Categorizer()

    def get_category(self, sql: str):
        ast = self.parser.parse(sql)
        tags = self.tag_extractor.extract_tags(ast)
        return self.categorizer.get_category(tags.tag_set)

    def get_sub_category(self, sql: str):
        ast = self.parser.parse(sql)
        tags = self.tag_extractor.extract_tags(ast)
        return self.categorizer.get_sub_category(tags.tag_set)
