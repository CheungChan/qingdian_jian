import os

import logzero
import pymysql

from qingdian_jian.settings import DEBUG

logfile = f"/tmp/{os.path.basename(__file__)}.log"
logzero.logfile(logfile, encoding='utf-8', maxBytes=500_0000, backupCount=3)
print(f'脚本DEBUG={DEBUG}')
test_db = {
    'db': 'qdbuluo',
    'host': '10.10.6.2',
    'user': 'develop',
    'password': '123-qwe',
    'charset': 'utf8mb4',
}
prod_db = {
    'db': 'qdbuluo',
    'host': '10.10.6.6',
    'port': 3306,
    'user': 'develop',
    'password': '123^%$-qwe',
    'charset': 'utf8mb4',
}
BL_MYSQL_CONF = test_db if DEBUG else prod_db
print(BL_MYSQL_CONF)
connection = None


def get_connection():
    global connection
    if not connection:
        connection = pymysql.connect(**BL_MYSQL_CONF)
    return connection


def executesql_and_fetchall(sql: str, *args):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql, args)
        return cursor.fetchall()


def main():
    sql1 = 'SELECT id FROM contents WHERE contents_refter_type = %s'
    cids = executesql_and_fetchall(sql1, (14,))
    print(cids)


if __name__ == '__main__':
    main()
