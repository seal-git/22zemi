from flask import request, jsonify

from app import my_app
from app.utils import reverse_sentence, generate_sentence
from app.db import db_random_generate


@my_app.route('/reverse', methods=['POST'])
# postされた文章を逆さ文にして返す
def reverse():
    json_data = request.json
    print(json_data)
    return jsonify({"result": reverse_sentence(json_data)})


@my_app.route('/reverse_random', methods=['POST'])
# ランダムに逆さの文章を返す
def reverse_random():
    result = db_random_generate("gutenberg_sentence")
    result = reverse_sentence(result["content"]["sentence"])
    return jsonify({"result": result})


@my_app.route('/random', methods=['POST'])
# ランダムに文章を返す
def random():
    return jsonify({"result": generate_sentence()})


@my_app.route('/db_sample_random_generate', methods=['POST'])
# ランダムにsample_db.gutenberg_sentenceから文章を返す
def db_sample_random_generate():
    result_dict = db_random_generate("gutenberg_sentence")
    return jsonify(result_dict)


@my_app.route('/get_feedback_yes_no', methods=['POST'])
# yes/noボタンが押されたらfeedbackとして処理する
def get_feedback_yes_no():
    json_data = request.json
    print(json_data)
    return 



