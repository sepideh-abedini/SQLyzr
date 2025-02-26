from typing import Any

from src.rel.db_facade import DatabaseFacade, DB_TIMEOUT


class DatabaseConnectionProxy:
    db_id: str
    facade: DatabaseFacade
    timeout: int

    def __init__(self, facade, db_id, timeout=DB_TIMEOUT):
        self.facade = facade
        self.db_id = db_id
        self.timeout = timeout

    def cursor(self):
        return DatabaseCursorProxy(self.facade, self.db_id, self.timeout)


class DatabaseCursorProxy:
    facade: DatabaseFacade
    db_id: str
    results: Any
    timeout: int

    def __init__(self, facade: DatabaseFacade, db_id, timeout: int):
        self.facade = facade
        self.db_id = db_id
        self.timeout = timeout

    def execute(self, sql: str):
        self.results = self.facade.exec_query_sync(self.db_id, sql, self.timeout)
        return self

    def fetchall(self):
        return self.results

    def __iter__(self):
        return iter(self.results)

    def close(self):
        pass
