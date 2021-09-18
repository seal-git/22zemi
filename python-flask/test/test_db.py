from app import app_
from flask import jsonify

"""
pytestはpython-flaskのルートディレクトリ(app.pyのあるところ)で`pytest ./test`と実行する．
"""


# def test_get_sample_db():
#     with app_.app_context():
#         result = get_sample_db()
#         assert(b"content" in result.data)
