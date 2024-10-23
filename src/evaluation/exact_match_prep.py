import sys
import json
# this file convert dev.json to dev.jsonfinal which append the db name at the end of each gold query
# this file contains a line for each gold query with refferd db name

def add_db_name_to_gold_sql(dev_json_path):
    with open (dev_json_path) as f:
        with open (dev_json_path+'.final', mode= 'w') as file:
            data = json.load(f)
            for e in data:
                file.write("{0}\t{1}\n".format(e["query"] if "query" in e else e["SQL"], e["db_id"]))