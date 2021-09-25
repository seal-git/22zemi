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
    
    # SPEED_UP_FLG
    #   Trueにすると高速化できるが、レコメンドの反映が遅れる
    #   RecommendSimpleなら NEXT_RESPONSE = True , RECOMMEND_PRIORITY = False 。
    #   RecommendSVM   なら NEXT_RESPONSE = False, RECOMMEND_PRIORITY = True  。
    NEXT_RESPONSE = False
    RECOMMEND_PRIORITY = True # RecommendSimpleでTrueにすると死にます

    RECOMMEND_METHOD = 'image'
    API_METHOD = 'yahoo'
    
    GET_GOOGLE_IMAGE = False
    USE_LOCAL_IMAGE = False
    USE_RAW_IMAGE = False
    MAX_DISTANCE = 200000  # 中心地からの距離 上限20
    RESPONSE_COUNT = 9  # 一回に返す店舗の数
    STOCK_COUNT = 80  # 検索で取得するデータの数．STOCK_COUNT個の店からRESPONSE_COUNT個選ぶ
    QUEUE_COUNT = 15  # レスポンスをキューで保持しておく最大数
    SET_OPEN_HOUR = True  # 開店時間固定する場合はTrueにする
    OPEN_HOUR = "18:00"  # 固定の開店時間
    LUNCH_TIME_START = 10  # ランチの開始時間
    LUNCH_TIME_END = 15  # ランチの終了時間
    MAX_LIST_COUNT = 10  # 画像の最大枚数

    IMAGE_DIRECTORY_PATH = 'data/image/'
    SERVER_URL = 'localhost' # 'reskima.com'
    INIT_DB = True  # Trueならば再起動時にDBをリセットする
    MAX_GOOGLE_IMAGES_COUNT = 4 # Google画像の取得枚数。最大10。大きくすると画像が多くなるがお金がかかる


    TEST = False  # test時はTrueにする
    if TEST:
        NEXT_RESPONSE = False
        RECOMMEND_PRIORITY = True  # RecommendSimpleでTrueにすると死にます

        RECOMMEND_METHOD = 'svm'
        API_METHOD = 'yahoo'

        GET_GOOGLE_IMAGE = True
        USE_LOCAL_IMAGE = True
        USE_RAW_IMAGE = False
        IMAGE_DIRECTORY_PATH = 'data/image/'
        SERVER_URL = 'localhost'
        MAX_DISTANCE = 200000  # 中心地からの距離 上限20
        RESPONSE_COUNT = 3  # 一回に返す店舗の数
        STOCK_COUNT = 50  # 検索で取得するデータの数．STOCK_COUNT個の店からRESPONSE_COUNT個選ぶ
        SET_OPEN_HOUR = True  # 開店時間固定する場合はTrueにする
        OPEN_HOUR = "12:00"  # 固定の開店時間
        MAX_GOOGLE_IMAGES_COUNT = 4 # Google画像の取得枚数。最大10。大きくすると画像が多くなるがお金がかかる
