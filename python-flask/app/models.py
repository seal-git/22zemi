from flask import request, jsonify

from app import my_app
from app.utils import reverse_sentence, generate_sentence

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
