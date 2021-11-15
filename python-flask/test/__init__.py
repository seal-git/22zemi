"""
全てのテストを実行したいときはルートディレクトリで`pytest -s`と実行する。
一部を実行したいときは`pytest test/(ファイル名) -s`と実行する。
"""

from app import config, database_functions

data = [
    (123456, 456789, "yahoo","yahoo"),
    (123456, 456790, "yahoo","yahoo"),
    (123456, 456791, "yahoo","yahoo"),
    (123457, 456789, "yahoo","yahoo") # 別グループ同ユーザー
]
for data_ in data:
    _ = database_functions.register_user_and_group_if_not_exist(*data_)