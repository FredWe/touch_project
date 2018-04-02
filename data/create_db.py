import sqlite3
import numpy as np
import io
import logging
import argparse
import os
import glob

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

def main():

    parser = argparse.ArgumentParser(
        description="find all .rec rawfile from argument DATADIR, \
            and convert all .rec path into db file at DBPATH")
    parser.add_argument("DBPATH", help="database file path")
    parser.add_argument("DATADIR", help="recfile directory path")
    args = parser.parse_args()
    logging.debug(args)
    DBPATH = args.DBPATH
    DATADIR = args.DATADIR
    if not DBPATH.endswith('.db'):
        raise ValueError('extension error')

    #csv store
    # Converts np.array to TEXT when inserting
    sqlite3.register_adapter(np.ndarray, adapt_array)
    # Converts TEXT to np.array when selecting
    sqlite3.register_converter("ARRAY", convert_array)

    conn = sqlite3.connect(DBPATH, detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    cur.execute("CREATE TABLE test (\
        id  INTEGER PRIMARY KEY AUTOINCREMENT,\
        machine_id  VARCHAR(20) NOT NULL,\
        operator    VARCHAR(20),\
        action  VARCHAR(40) NOT NULL,\
        internal_id VARCHAR(20),\
        action_interval FLOAT,\
        data_raw    ARRAY,\
        data_baseline   ARRAY,\
        data_diff   ARRAY   NOT NULL,\
        data_ticking ARRAY,\
        data_onMask ARRAY\
        )")

    recfiles = glob.glob(os.path.join(DATADIR, '**', '*.rec'), recursive=True)
    for filepath in recfiles:
        if ' ' in filepath:
            raise ValueError('%s\nthis filepath contains space' % filepath)
    
    

    # 关闭Cursor:
    cur.close()
    # 提交事务:
    conn.commit()
    # 关闭Connection:
    conn.close()

if __name__ == '__main__':
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
    main()
