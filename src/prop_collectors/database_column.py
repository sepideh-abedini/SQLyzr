from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class DatabaseColumn:
    table: str
    name: str
    type: str

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.table}.{self.name}:{self.type}"


STAR_COLUMN = DatabaseColumn('', '*', '')
