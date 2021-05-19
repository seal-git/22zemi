from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from flask import jsonify
from app import my_app, db
import pymysql.cursors
# from flask_marshmallow import Marshmallow

# ma = Marshmallow()

conn = pymysql.connect(
    host = 'mysql',
    port = 3306,
    user = 'sample_user',
    password = 'pass',
    database = 'sample_db'
)

conn.ping(reconnect=True)
if conn.open:
    print("connected!")

@my_app.route('/db_sample_random_generate', methods=['POST'])
def db_sample_random_generate():
    with conn.cursor() as cur:
        # sql = "DESC employee"
        sql = "SHOW DATABASES"
        cur.execute(sql)
        rows = cur.fetchall()
        print(rows)
        return jsonify(rows)




