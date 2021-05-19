from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import app.config


my_app = Flask(__name__)
my_app.config.from_object(config.Config)

# アプリでDB操作を行えるように初期設定する
db = SQLAlchemy(my_app)
db.init_app(my_app)

import app.make_html

import app.views
import app.models
import app.db


