import os, sys
import json
import sqlite3
import argparse
import lib
import pandas as pd
import csv

def read_pred_sql(pred_sql_path):
    pred_sql_strs = []
    with open(pred_sql_path) as file:
        while line := file.readline():
            pred_sql_strs.append(line.rstrip())
    return pred_sql_strs

def read_gold_data(dev_json):
    gold_dbs = []
    gold_sql_strs = []
    with open(dev_json) as f:
        json_data = json.load(f)
        for e in json_data:
            gold_dbs.append(e['db_id'])
            gold_sql_strs.append(e['query'] if 'query' in e else e['SQL'])
    return gold_dbs, gold_sql_strs

def exec_sql(db_path, sql):
    """
    return 1 if the values between prediction and gold are matching
    in the corresponding index. Currently not support multiple col_unit(pairs).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        return res
    except sqlite3.OperationalError as e:
        # print("******************** SQL EXECUTION FAILUER: ", db_path)
        # print(sql)
        # print(e)
        # print("******************** SQL EXECUTION FAILUER: ", db_path)
        return False
    
def eval_exec_acc(db_path, gold_sql, pred_sql, temp):
    gold_sql_exec_res = exec_sql(db_path, gold_sql)
    timer = lib.Timer()
    timer.start()
    
    pred_sql_exec_res = exec_sql(db_path, pred_sql)
    pred_sql_exec_time = timer.stop()
    result = pred_sql_exec_res == gold_sql_exec_res
    # if not result:
        # print("********************* Pred:", db_path)
        # print(pred_sql)
        # print("********************* Gold:", db_path)
        # print(gold_sql)
    
    errors = pd.DataFrame([{"temp" : temp,
                            "gold" : gold_sql,
                            "pred" : pred_sql}])
    errors.to_csv("errors.csv", mode ='a', sep='\t')
    
    return result, pred_sql_exec_time