from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template("index.html", result="")


@app.route('/action', methods=['POST'])
def action():
    json_data = request.json
    print(json_data)
    return render_template("index.html", result='aaa')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)  # debug=Trueで自動更新されるようになる
