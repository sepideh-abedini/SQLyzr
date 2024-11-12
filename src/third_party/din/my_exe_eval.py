import os, sys
import json
import sqlite3



def exec_db(db, q):
    """
    return 1 if the values between prediction and gold are matching
    in the corresponding index. Currently not support multiple col_unit(pairs).
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute(q)
        res = cursor.fetchall()
        return res
    except:
        return False
    
def eval(db, g, p):
    q_res = exec_db(db, p)
    g_res = exec_db(db, g)
    
    
def main():
    db = "/Users/spnaz/spider/ConcatDB/{db_name}/{db_name}.sqlite".format(db_name="concert_singer")
    p = "SELECT singer, concert FROM singer"
    g = 'SELECT concert, singer FROM singer'
    eval(db, g, p)


if __name__ == "__main__":
    main()