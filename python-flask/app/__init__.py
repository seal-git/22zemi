from flask import Flask
from flask_cors import CORS
from app import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app_ = Flask(__name__, static_folder='../static', static_url_path='/static')
app_.config.from_object(config.Config)
# CORS(app_)

# アプリ用の設定を出力
print("===application config===")
for key, value in config.MyConfig.__dict__.items():
    if not key.startswith("__"): print(f"{key}: {value}")
print("========================")

# アプリでDB操作を行えるように初期設定する
db_ = SQLAlchemy(app_)
db_.init_app(app_)

migrate = Migrate(app_, db_)

import app.models
