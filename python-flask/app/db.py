from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from flask import jsonify
from app import my_app, db
# import pymysql.cursors
import mysql.connector
from random import randint
# from flask_marshmallow import Marshmallow

# ma = Marshmallow()

conn = mysql.connector.connect(
    host = 'mysql', #docker-compose.ymlで指定したコンテナ名
    port = 3306,
    user = 'root',
    password = 'pass',
    database = 'sample_db'
)

conn.ping(reconnect=True)
if conn.is_connected():
    print("connected!")


def db_random_generate(table):
    '''
    :param table:(str)table name
    :return: (dict) one row of the table
    '''
    conn.ping(reconnect=True)

    if table is None:
        raise(Exception("must have table name"))
    # conn.ping(reconnect=True)
    cur = conn.cursor(dictionary=True)
    # get primary key name
    sql = f"""\
        SELECT COLUMN_NAME AS 'key' FROM information_schema.columns \
        WHERE TABLE_NAME='{table}' AND COLUMN_KEY='PRI'\
        """
    # print(sql)
    cur.execute(sql)
    key = cur.fetchone()["key"]

    # get random one
    sql = f"""\
        SELECT COUNT({key}) AS 'count' FROM {table}\
        """
    # print(sql)
    cur.execute(sql)
    rows_num = cur.fetchone()["count"]
    rand_idx = randint(0, rows_num-1)
    sql = f"""\
        SELECT * FROM {table} WHERE {key}={rand_idx}
    """
    cur.execute(sql)
    content = cur.fetchone()
    result = {
        "keys": list(content.keys()),
        "content": content
    }
    cur.close()
    return result




