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
    query = Column('query', String(100)) # 検索条件 # フリーワード
    max_dist = Column('max_dist', Float) # 検索条件 # 距離上限
    open_day = Column('open_day', Date) # 検索条件 # 日付
    open_hour = Column('open_hour', Time) # 検索条件 # 時間
    open_now = Column('open_now', Boolean) # 検索条件 # 時間
    max_price = Column('max_price', Integer) # 検索条件 # 金額上限
    min_price = Column('min_price', Integer) # 検索条件 # 金額下限
    loco_mode = Column('loco_mode', Boolean)
    image = Column('image', Boolean)
    start = Column('start', Integer)  # 取得開始位置
    sort = Column('sort', String(50)) # 検索条件 # 表示順
    recommend_method = Column('recommend_method', String(50)) # 検索条件 # レコメンド
    api_method = Column('api_method', String(50)) # 検索条件 # レコメンド
    price_average = Column('group_price', Float) # レコメンド # 平均価格
    distance_average = Column('group_distance', Float) # レコメンド # 平均距離
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    password = Column('password', String(50)) # パスワード (2021/08/21 未使用)

# レストラン
# TODO: businessHourを曜日ごとにする
class Restaurant(Base):
    __tablename__ = 'restaurants'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', String(50), primary_key=True)
    yahoo_id = Column('yahoo_id', String(50))
    google_id = Column('google_id', String(50))
    name = Column('name', String(100)) # 店名
    address = Column('address', String(400)) # 住所
    lat = Column('lat', Float) # 緯度
    lon = Column('lon', Float) # 経度
    station = Column('station', String(400)) # 駅名リスト(\n区切り)
    railway = Column('railway', String(400)) # 路線リスト(\n区切り)
    phone = Column('phone', String(20)) # 電話番号
    genre_name = Column('genre_name', String(200)) # ジャンル名リスト(\n区切り)
    genre_code = Column('genre_code', String(200)) # ジャンルコード: Yahoo Local Search API を参照(\n区切り)
    lunch_price = Column('lunch_price', Integer) # 昼食の価格帯
    dinner_price = Column('dinner_price', Integer) # 夕食の価格帯
    monday_opening_hours = Column('monday_opening_hours', String(100))
    tuesday_opening_hours = Column('tueday_opening_hours', String(100))
    wednesday_opening_hours = Column('wednesday_opening_hours', String(100))
    thursday_opening_hours = Column('thursday_opening_hours', String(100))
    friday_opening_hours = Column('friday_opening_hours', String(100))
    saturday_opening_hours = Column('saturday_opening_hours', String(100))
    sunday_opening_hours = Column('sunday_opening_hours', String(100))
    access = Column('access', String(400))
    catchcopy = Column('catchcopy', String(400)) # キャッチコピー
    health_info = Column('health_info', String(400))
    web_url = Column('url_web', String(400)) # お店のURL
    map_url = Column('url_map', String(400)) # MapのURL
    yahoo_rating_str = Column('yahoo_rating_str', String(100)) # yahoo評価値
    yahoo_rating_float = Column('yahoo_rating_float', Float) # yahoo評価値(出力用文字列)
    google_rating = Column('google_rating', Float)
    review = Column('yahoo_review', String(2000)) # レビュー文字列(\t区切り。\nではない。)
    image_url = Column('image_url', String(2000)) # 写真url(\n区切り)
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
    votes_like = Column('votes_like', Integer) # -1: 未送信 # session.query(History).filter(History.group==group_id, History.restaurant==restaurants_info[i]['Restaurant_id'], History.feeling==True).count() # レストランのいいね数
    votes_all = Column('votes_all', Integer) # -1: 未送信 # session.query(History).filter(History.group==group_id, History.restaurant==restaurants_info[i]['Restaurant_id'], History.feeling is not None).count() # レストランの投票人数
    number_of_participants = Column('number_of_participants', Integer) # 投票参加人数
    recommend_priority = Column('recommend_priority', Float)
    price = Column('price', Integer) # グループごとの時間帯の値段
    opening_hours = Column('opening_hours', String(50)) # グループごとの時間帯の営業時間
    distance_float = Column('distance_float', Float)  # 現在地からの距離
    distance_str = Column('distance_str', String(50))  # 現在地からの距離(出力用)
    recommend_score = Column('recommend_score', Float)
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)


# ============================================================================================================
# INIT_DBがTrueならDBを初期化する
if config.MyConfig.INIT_DB: 
    Base.metadata.drop_all(ENGINE)
Base.metadata.create_all(ENGINE)  # create tables
Base.query = session.query_property()
