import subprocess
res = subprocess.call('pipenv install --system', shell=True)
print(res)

from app.flask import Flask, render_template, request, jsonify
from app.utils import reverse_sentence, generate_sentence
from app import app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)  # debug=Trueで自動更新されるようになる
