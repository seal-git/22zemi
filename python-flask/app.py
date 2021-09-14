import os
import subprocess

res = subprocess.call('pipenv install --system', shell=True)
print(res)

import yaml
with open(".flask-env.dev.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
for key,value in config.items():
    os.environ[key] = str(value)

from app import app_

if __name__ == '__main__':
    app_.run(host="0.0.0.0", port=5000)  #
    # debug=Trueで自動更新されるようになる
