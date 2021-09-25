"""
全てのテストを実行したいときはルートディレクトリで`pytest -s`と実行する。
一部を実行したいときは`pytest test/(ファイル名) -s`と実行する。
"""

from app import config, database_functions

_, _, _, _, _ = database_functions.register_user_and_group_if_not_exist(123,
                                                                  456789,
                                                                  "新宿駅",
                                                                  "yahoo",
                                                                  "yahoo")