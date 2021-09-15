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
    RESULTS_COUNT = 3  # 一回に返す店舗の数
    STOCK_COUNT = 15  # 検索で取得するデータの数．STOCK_COUNT個の店からRESULTS_COUNT個選ぶ
    RECOMMEND_METHOD = "queue"  # レコメンド関数
    SET_OPEN_HOUR = True  # 開店時間固定
    OPEN_HOUR = "12:00"

class TestConfig:
    USE_LOCAL_IMAGE = True
    USE_RAW_IMAGE = False
    MAX_DISTANCE = 200000  # 中心地からの距離 上限20
    RESULTS_COUNT = 3  # 一回に返す店舗の数
    STOCK_COUNT = 100  # 検索で取得するデータの数．STOCK_COUNT個の店からRESULTS_COUNT個選ぶ
    RECOMMEND_METHOD = "queue"  # レコメンド関数 