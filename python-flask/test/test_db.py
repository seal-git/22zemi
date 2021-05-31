from app.db import db_random_generate
from app import my_app
from flask import jsonify

def test_db_gutenberg_information_random_generate():
    with my_app.app_context():
        result = db_random_generate("gutenberg_information")
        assert(len(result["content"]) == 7)

def test_db_gutenberg_sentence():
    with my_app.app_context():
        result = db_random_generate("gutenberg_sentence")
        assert(len(result["content"]) == 3)
