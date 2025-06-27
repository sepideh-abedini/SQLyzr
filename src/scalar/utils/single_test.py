import sqlite3
import pandas as pd
import tqdm
from sdv.metadata import Metadata
from sdv.multi_table import HMASynthesizer
from sdv.utils import drop_unknown_references

from synth.parser import parse_sql
from synth.sdv_visitor import SDVMetadataVisitor

from sqlalchemy import create_engine
import pandas as pd

db_id = "works_cycles"
metadata = Metadata.load_from_json(f'data/database/{db_id}/tables_schema.json')

m = metadata.get_table_metadata('Customer')

print(metadata._get_all_foreign_keys(""))
