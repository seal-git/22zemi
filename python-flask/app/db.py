from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from app import db
import pymysql.cursors
# from flask_marshmallow import Marshmallow

# ma = Marshmallow()

conn = pymysql.connect(
    host = 'mysql',
    port = 3306,
    user = 'sample_user',
    password = 'mrpass',
    database = 'sample-db'
)

conn.ping(reconnect=True)
print(conn.is_connected())



