from geopy import distance
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import TIMESTAMP as Timestamp
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.sql.expression import text
import os

from app import config

DATABASE = 'mysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (
    "root", # user_name
    os.environ['MYSQL_ROOT_PASSWORD'], # password
    'mysql', # host_ip
    '3306', # port
    'reskima_db' # db_name
)
ENGINE = create_engine(
    DATABASE,
    encoding = "utf-8",
    echo=False, # Trueだと実行のたびにSQLが出力される
    max_overflow=-1
)

session = scoped_session(
    sessionmaker(
        autocommit = False,
        autoflush = False,
        bind = ENGINE
    )
)

# modelで使用する
Base = declarative_base()

# ============================================================================================================

# ユーザ
class User(Base):
    __tablename__ = 'users'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))
    email = Column('email', String(100)) # メールアドレス (2021/08/21 未使用)
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    password = Column('password', String(50)) # パスワード (2021/08/21 未使用)


# グループ
class Group(Base):
    __tablename__ = 'groups'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', Integer, primary_key=True)
    lat = Column('lat', Float, nullable=False) # 緯度
    lon = Column('lon', Float, nullable=False) # 経度
    address = Column('address', String(100), nullable=False) # 住所
    max_dist = Column('max_dist', Float) # 検索条件 # 距離上限
    query = Column('query', String(100)) # 検索条件 # フリーワード
    genre = Column('genre', String(50)) # 検索条件 # ジャンル
    open_day = Column('open_day', Date) # 検索条件 # 日付
    open_hour = Column('open_hour', Time) # 検索条件 # 時間
    max_price = Column('max_price', Integer) # 検索条件 # 金額上限
    min_price = Column('min_price', Integer) # 検索条件 # 金額下限
    sort = Column('sort', String(50)) # 検索条件 # 表示順
    recommend_method = Column('recommend_method', String(50), nullable=False) # 検索条件 # レコメンド
    api_method = Column('api_method', String(50), nullable=False) # 検索条件 # レコメンド
    price_average = Column('group_price', Float) # レコメンド # 平均価格
    distance_average = Column('group_distance', Float) # レコメンド # 平均距離
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    start = Column('start', Integer)  # 取得開始位置
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    password = Column('password', String(50)) # パスワード (2021/08/21 未使用)

# レストラン
# TODO: businessHourを曜日ごとにする
class Restaurant(Base):
    __tablename__ = 'restaurants'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', String(50), primary_key=True)
    name = Column('name', String(100), nullable=False) # 店名
    address = Column('address', String(400), nullable=False) # 住所
    lat = Column('lat', Float, nullable=False) # 緯度
    lon = Column('lon', Float, nullable=False) # 経度
    catchcopy = Column('catchcopy', String(400)) # キャッチコピー
    price = Column('price', Integer) # 価格帯
    lunch_price = Column('lunch_price', Integer) # 昼食の価格帯
    dinner_price = Column('dinner_price', Integer) # 夕食の価格帯
    category = Column('category', String(400)) # カテゴリー
    url_web = Column('url_web', String(400)) # お店のURL
    url_map = Column('url_map', String(400)) # MapのURL
    review_rating_str = Column('review_rating_str', String(100)) # 顧客レビューの評価値
    review_rating_float = Column('review_rating_float', Float) # 顧客レビューの評価値
    business_hour = Column('business_hour', String(400)) # 営業時間
    open_hour = Column('open_hour', Float) # 開店時間
    close_hour = Column('close_hour', Float) # 閉店時間
    genre_code = Column('genre_code', String(200)) # ジャンルコード: Yahoo Local Search API を参照
    genre_name = Column('genre_name', String(200)) # ジャンル名
    images = Column('images', String(5000)) # 写真
    menu = Column('menu', String(400)) # メニュー (2021/08/21 未使用)
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)


# 所属。ユーザがどのグループに所属しているか
class Belong(Base):
    __tablename__ = 'belongs'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    user = Column('user', Integer, primary_key=True)
    group = Column('group', Integer, primary_key=True)
    request_count = Column('request_count', Integer, nullable=False, server_default='0') # レコメンド # リクエスト回数
    request_restaurants_num = Column('request_restaurants_num', Integer, nullable=False, server_default='0') # レコメンド # レストランを受け取った数
    next_response = Column('next_response', String(16000)) # 次のレスポンスをあらかじめ検索して新しい順に保持する
    writable = Column('writable', Boolean, nullable=False, default=True) # スレッドで検索している途中でリクエストが来たときのために，排他処理をする
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)

# 履歴。ユーザのfeeling
# ユーザに送信した店舗の履歴。
class History(Base):
    __tablename__ = 'histories'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    user = Column('user', Integer, primary_key=True)
    group = Column('group', Integer, primary_key=True)
    restaurant = Column('restaurant', String(50), primary_key=True)
    feeling = Column('feeling', Boolean) # None: 表示したが未回答, True: いいね, False: 悪いね
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)

# レコメンドの候補として取得した店と，投票数
class Vote(Base):
    __tablename__ = 'votes'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    group = Column('group', Integer, primary_key=True)
    restaurant = Column('restaurant', String(50), primary_key=True)
    votes_like = Column('votes_like', Integer, nullable=False) # -1: 未送信 # session.query(History).filter(History.group==group_id, History.restaurant==restaurants_info[i]['Restaurant_id'], History.feeling==True).count() # レストランのいいね数
    votes_all = Column('votes_all', Integer, nullable=False) # -1: 未送信 # session.query(History).filter(History.group==group_id, History.restaurant==restaurants_info[i]['Restaurant_id'], History.feeling is not None).count() # レストランの投票人数
    recommend_priority = Column('recommend_priority', Float)
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)


# ============================================================================================================
# INIT_DBがTrueならDBを初期化する
# if config.MyConfig.INIT_DB: 
Base.metadata.drop_all(ENGINE)
Base.metadata.create_all(ENGINE)  # create tables
Base.query = session.query_property()
