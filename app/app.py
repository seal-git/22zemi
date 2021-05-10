from flask import Flask, render_template, request, jsonify
from utils import reverse

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template("index.html")


@app.route('/action', methods=['POST'])
def action():
    json_data = request.json
    print(json_data)
    return jsonify({"result": reverse(json_data)})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)  # debug=Trueで自動更新されるようになる
