from app import app_
import subprocess

res = subprocess.call('pipenv install --system', shell=True)

if __name__ == '__main__':
    app_.run(host="0.0.0.0", port=5000, debug=True)  #
    # debug=Trueで自動更新されるようになる
