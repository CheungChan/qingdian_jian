import os

import logzero
import records

from qingdian_jian.settings import DEBUG

logfile = f"/tmp/{os.path.basename(__file__)}.log"
logzero.logfile(logfile, encoding='utf-8', maxBytes=500_0000, backupCount=3)
print(f'脚本DEBUG={DEBUG}')
TEST_MYSQL_URL = 'mysql://10.10.6.2/qdbuluo?user=develop&password=123-qwe&charset=utf8mb4'
PROD_MYSQL_URL = 'mysql://10.10.6.6/qdbuluo?user=develop&password=123^%$-qwe&charset=utf8mb4'
MYSQL_URL = TEST_MYSQL_URL if DEBUG else PROD_MYSQL_URL
db = records.Database(MYSQL_URL)


def main():
    tags = db.query('select * from tag limit 10').as_dict()
    print(tags)


if __name__ == '__main__':
    main()
