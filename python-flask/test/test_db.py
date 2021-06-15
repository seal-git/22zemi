from app.models import get_sample_db
from app import app_
from flask import jsonify


def test_get_sample_db():
    with app_.app_context():
        result = get_sample_db()
        assert(b"content" in result.data)
