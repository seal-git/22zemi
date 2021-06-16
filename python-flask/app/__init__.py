from flask import Flask
from flask_cors import CORS
import app.config
from flask_sqlalchemy import SQLAlchemy 

app_ = Flask(__name__)
app_.config.from_object(config.Config)
CORS(app_)

# アプリでDB操作を行えるように初期設定する
db_ = SQLAlchemy(app_)
db_.init_app(app_)

import app.models
