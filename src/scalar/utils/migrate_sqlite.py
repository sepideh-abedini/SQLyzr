import sqlite3
import os
from typing import List, Tuple

def exec_sql(file: str, sql: str) -> List[Tuple]:
    """Execute SQL on a SQLite database and return the results."""
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    res = cursor.execute(sql).fetchall()
    conn.close()
    return res

def get_table_info(file: str, table: str) -> List[Tuple]:
    """Get information about a table's columns."""
    return exec_sql(file, f"PRAGMA table_info('{table}')")

def has_primary_key(file: str, table: str) -> bool:
    """Check if a table has a primary key."""
    columns = get_table_info(file, table)
    pk_columns = [col[1] for col in columns if col[5] > 0]
    return len(pk_columns) > 0

def get_primary_key_columns(file: str, table: str) -> List[str]:
    """Get the primary key columns for a table."""
    columns = get_table_info(file, table)
    return [col[1] for col in columns if col[5] > 0]

def generate_migration_sql(sqlite_file: str, output_file: str = None) -> str:
    """
    Generate a migration SQL script for a SQLite database.
    
    The migration adds a new table_name_pk column to each table as the primary key
    and removes the existing primary key.
    
    Args:
        sqlite_file: Path to the SQLite database file
        output_file: Path to save the migration SQL script (optional)
        
    Returns:
        The generated migration SQL script
    """
    # Get all tables in the database
    tables = [row[0] for row in exec_sql(sqlite_file, "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    
    migration_lines = []
    
    for table in tables:
        # Get table columns and primary key information
        columns = get_table_info(sqlite_file, table)
        pk_columns = get_primary_key_columns(sqlite_file, table)
        
        # Skip tables without primary keys
        if not pk_columns:
            continue
        
        new_pk = f"{table}_pk"
        
        # Build column definitions for the new table
        col_defs = []
        for col in columns:
            name = col[1]
            col_type = col[2]
            not_null = "NOT NULL" if col[3] == 1 else ""
            default = f"DEFAULT {col[4]}" if col[4] is not None else ""
            
            # Remove primary key constraint from original columns
            if name in pk_columns:
                col_defs.append(f'{name} {col_type} {not_null} {default}'.strip())
            else:
                col_defs.append(f'{name} {col_type} {not_null} {default}'.strip())
        
        # Add the new primary key column
        col_defs.append(f'{new_pk} TEXT PRIMARY KEY')
        
        # Build column names for the INSERT statement
        col_names = [col[1] for col in columns]
        
        # Build the expression to generate the new primary key value
        if len(pk_columns) == 1:
            # Single column primary key
            concat_expr = f"CAST({pk_columns[0]} AS TEXT)"
        else:
            # Composite primary key
            concat_expr = " || '-' || ".join([f'CAST({col} AS TEXT)' for col in pk_columns])
        
        new_col_names = col_names + [f'{concat_expr} AS {new_pk}']
        
        # Generate migration SQL
        migration_lines.append(f"-- Migration for table {table}")
        migration_lines.append(f"ALTER TABLE {table} RENAME TO {table}_old;")
        migration_lines.append(
            f"CREATE TABLE {table} (\n  {',\n  '.join(col_defs)}\n);"
        )
        migration_lines.append(
            f"INSERT INTO {table} ({', '.join(col_names)}, {new_pk})\n"
            f"SELECT {', '.join(new_col_names)} FROM {table}_old;"
        )
        migration_lines.append(f"DROP TABLE {table}_old;\n")
    
    migration_sql = "\n".join(migration_lines)
    
    # Save to file if output_file is provided
    if output_file:
        with open(output_file, "w") as f:
            f.write(migration_sql)
    
    return migration_sql

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate_sqlite.py <sqlite_file> [output_file]")
        sys.exit(1)
    
    sqlite_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    migration_sql = generate_migration_sql(sqlite_file, output_file)
    
    if not output_file:
        print(migration_sql)