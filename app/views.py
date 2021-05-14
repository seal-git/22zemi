from app import app


@app.route('/')
def top():
    return render_template("index.html")


@app.route('/reverse')
def reverse():
    return render_template("reverse.html")


@app.route('/reverse', methods=['POST'])
def action():
    json_data = request.json
    print(json_data)
    return jsonify({"result": reverse_sentence(json_data)})


@app.route('/reverse_random', methods=['POST'])
def reverse_random():
    result = generate_sentence()
    result = reverse_sentence(result)
    return jsonify({"result": result})


@app.route('/random', methods=['POST'])
def random():
    return jsonify({"result": generate_sentence()})
