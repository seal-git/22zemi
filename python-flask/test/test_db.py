from app.db import db_sample_random_generate
from flask import json

def test_db_sample_random_generate():
    result = db_sample_random_generate()
    print(json.load(result))
