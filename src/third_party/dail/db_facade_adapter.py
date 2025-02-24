from typing import Any

from src.rel.db_facade import DatabaseFacade


class DatabaseConnectionProxy:
    db_id: str
    facade: DatabaseFacade

    def __init__(self, facade, db_id):
        self.facade = facade
        self.db_id = db_id

    def cursor(self):
        return DatabaseCursorProxy(self.facade, self.db_id)


class DatabaseCursorProxy:
    facade: DatabaseFacade
    db_id: str
    results: Any

    def __init__(self, facade: DatabaseFacade, db_id):
        self.facade = facade
        self.db_id = db_id

    def execute(self, sql: str):
        self.results = self.facade.exec_query_sync(self.db_id, sql)
        return self

    def fetchall(self):
        return self.results

    def __iter__(self):
        return iter(self.results)

    def close(self):
        pass
