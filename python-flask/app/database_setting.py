from geopy import distance
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import TIMESTAMP as Timestamp
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.sql.expression import text
import os


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
    echo=True # Trueだと実行のたびにSQLが出力される
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


# ユーザ
class User(Base):
    __tablename__ = 'users'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))
    email = Column('email', String(100))
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    password = Column('password', String(50))


# グループ
class Group(Base):
    __tablename__ = 'groups'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', Integer, primary_key=True)
    lat = Column('lat', Float, nullable=False) # 検索条件 # 緯度
    lon = Column('lon', Float, nullable=False) # 検索条件 # 経度
    address = Column('address', String(100), nullable=False) # 検索条件 # 住所
    max_dist = Column('max_dist', Float) # 検索条件 # 距離上限
    query = Column('query', String(100)) # 検索条件 # フリーワード
    genre = Column('genre', String(50)) # 検索条件 # ジャンル
    open_day = Column('open_day', Date) # 検索条件 # 日付
    open_hour = Column('open_hour', Time) # 検索条件 # 時間
    max_price = Column('max_price', Integer) # 検索条件 # 金額上限
    min_price = Column('min_price', Integer) # 検索条件 # 金額下限
    sort = Column('sort', String(50)) # 検索条件 # 表示順
    recommend_method = Column('recommend_method', String(50)) # 検索条件 # レコメンド
    group_price = Column('group_price', Integer) # レコメンド # 平均価格
    group_distance = Column('group_distance', Float) # レコメンド # 平均距離
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    password = Column('password', String(50))


# レストラン
class Restaurant(Base):
    __tablename__ = 'restaurants'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', String(50), primary_key=True)
    name = Column('name', String(100), nullable=False)
    address = Column('address', String(400), nullable=False)
    lat = Column('lat', Float, nullable=False)
    lon = Column('lon', Float, nullable=False)
    catchcopy = Column('catchcopy', String(400))
    price = Column('price', Integer)
    lunch_price = Column('lunch_price', Integer)
    dinner_price = Column('dinner_price', Integer)
    category = Column('category', String(400))
    url_yahoo_loco = Column('url_yahoo_loco', String(400))
    url_yahoo_map = Column('url_yahoo_map', String(400))
    review_rating = Column('review_rating', String(100))
    business_hour = Column('business_hour', String(400))
    open_hour = Column('open_hour', Float)
    close_hour = Column('close_hour', Float)
    genre_code = Column('genre_code', String(200))
    genre_name = Column('genre_name', String(200))
    images = Column('images', String(800))
    menu = Column('menu', String(400))
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)


# 所属．ユーザがどのグループに所属しているか
class Belong(Base):
    __tablename__ = 'belongs'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    user = Column('user', Integer, primary_key=True)
    group = Column('group', Integer, primary_key=True)
    request_count = Column('request_count', Integer, nullable=False, server_default='0') # レコメンド # リクエスト回数
    request_restaurants_num = Column('request_restaurants_num', Integer, nullable=False, server_default='0') # レコメンド # レストランを受け取った数
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)

# 履歴．ユーザのfeeling
class History(Base):
    __tablename__ = 'histories'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    user = Column('user', Integer, primary_key=True)
    group = Column('group', Integer, primary_key=True)
    restaurant = Column('restaurant', String(50), primary_key=True)
    feeling = Column('feeling', Boolean)
    created_at = Column('created_at', Timestamp, server_default=current_timestamp(), nullable=False)
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)


Base.metadata.drop_all(ENGINE)
Base.metadata.create_all(ENGINE) # create tables
Base.query = session.query_property()
