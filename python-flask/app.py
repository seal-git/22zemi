import subprocess
from datetime import datetime, timezone, timedelta

# パッケージインストールの自動実行
res = subprocess.call('pipenv install --system', shell=True)

# マイグレーションの自動実行
# 詳しくはmigrations/READMEを参照
now = datetime.now(tz=timezone(timedelta(hours=9)))
message = now.strftime("%Y%m%d%H%M%S")
cmd = f'alembic revision --autogenerate -m "{message}"'
cmd += ' && alembic upgrade head'
res = subprocess.call(cmd, shell=True)


from app import app_
if __name__ == '__main__':
    app_.run(host="0.0.0.0", port=5000)  #
    # debug=Trueで自動更新されるようになる
