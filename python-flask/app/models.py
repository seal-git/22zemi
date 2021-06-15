from sqlalchemy import *
from flask import jsonify
from app import app_, db_
import mysql.connector
from random import randint

"""
mysqlサーバーとの接続はmysql.connectorで行っているが，SQLAlchemyへ換装したい．
"""

# mysqlサーバーと接続
conn = mysql.connector.connect(
    host = 'mysql', #docker-compose.ymlで指定したコンテナ名
    port = 3306,
    user = 'root',
    password = 'pass',
    database = 'sample_db'
)

# mysqlサーバーとの接続を確認
conn.ping(reconnect=True)
if conn.is_connected():
    print("db connected!")


@app_.route('/get_sample_db', methods=['POST'])
# ランダムにsample_db.sample_tableから一つ取得
def get_sample_db():
    conn.ping(reconnect=True)  # 接続が途切れた時に再接続する

    cur = conn.cursor(dictionary=True)

    # keyからランダムに一つ取得
    rand_idx = randint(1, 6)
    sql = ("SELECT * "
           "FROM sample_table "
           f"WHERE user_id={rand_idx}")
    cur.execute(sql)
    content = cur.fetchone()
    result = {
        "keys": list(content.keys()),
        "content": content
    }
    cur.close()
    return jsonify(result)


