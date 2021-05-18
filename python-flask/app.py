import subprocess

res = subprocess.call('pipenv install --system', shell=True)
print(res)

from app import my_app

if __name__ == '__main__':
    my_app.run(host="0.0.0.0", port=5000, debug=True)  # debug=Trueで自動更新されるようになる
