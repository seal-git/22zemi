from flask import request, jsonify

from app import my_app
from app.utils import reverse_sentence, generate_sentence
from app.db import db_random_generate

@my_app.route('/reverse', methods=['POST'])
def reverse():
    json_data = request.json
    print(json_data)
    return jsonify({"result": reverse_sentence(json_data)})


@my_app.route('/reverse_random', methods=['POST'])
def reverse_random():
    result = generate_sentence()
    result = reverse_sentence(result)
    return jsonify({"result": result})


@my_app.route('/random', methods=['POST'])
def random():
    return jsonify({"result": generate_sentence()})


@my_app.route('/db_sample_random_generate', methods=['POST'])
def db_sample_random_generate():
    result_dict = db_random_generate("gutenberg_sentence")
    return jsonify(result_dict)


