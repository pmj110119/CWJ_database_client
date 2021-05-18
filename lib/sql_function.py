import pymysql
import numpy as np

def search_id(curser,table_name):
    sql = 'select * from '+table_name
    cursor.execute(sql)

    ret = np.array(cursor.fetchall())
    print(ret[-1][2][1:])
    # for data in ret:
    #     if not data:
    #         continue
    #     print(data[2][1:])
    #     print(data[2][1:])