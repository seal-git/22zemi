from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

# アプリでDB操作を行えるように初期設定する
def init_db(app):
  db.init_app(app)