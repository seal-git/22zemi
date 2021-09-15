# Flaskで読み込む設定
class Config:
    import os
    # Flask
    DEBUG = True

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'mysql://{user}:{password}@{host}/flask_sample?charset=utf8'.format(
        **{
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_ROOT_PASSWORD', ''),
            'host': os.getenv('localhost'),
        })
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


# アプリ内で使うオリジナルの設定
class MyConfig:
    USE_LOCAL_IMAGE = False
    USE_RAW_IMAGE = False
    MAX_DISTANCE = 200000  # 中心地からの距離 上限20
    RESPONSE_COUNT = 3  # 一回に返す店舗の数
    SEARCH_COUNT = 15  # 検索で取得するデータの数．SEARCH_COUNT個の店からRESPONSE_COUNT個選ぶ
    RECOMMEND_METHOD = "simple"  # レコメンドメソッド
    SET_OPEN_HOUR = True  # 開店時間固定する場合はTrueにする
    OPEN_HOUR = "12:00"  # 固定の開店時間


# pytest実行時に読まれる設定
class TestConfig:
    USE_LOCAL_IMAGE = True
    USE_RAW_IMAGE = False
    MAX_DISTANCE = 200000  # 中心地からの距離 上限20
    RESPONSE_COUNT = 3  # 一回に返す店舗の数
    SEARCH_COUNT = 15  # 検索で取得するデータの数．SEARCH_COUNT個の店からRESPONSE_COUNT個選ぶ
    RECOMMEND_METHOD = "queue"  # レコメンドメソッド
    SET_OPEN_HOUR = True  # 開店時間固定する場合はTrueにする
    OPEN_HOUR = "12:00"  # 固定の開店時間
