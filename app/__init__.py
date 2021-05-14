from flask import Flask
import app.views
import app.db


app = Flask(__name__)

db.init_app(app)