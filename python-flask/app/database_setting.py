from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import TIMESTAMP as Timestamp
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.sql.expression import text
import os


DATABASE = 'mysql://%s:%s@%s/%s?charset=utf8mb4' % (
    "root", # user_name
    os.environ['MYSQL_ROOT_PASSWORD'], # password
    'localhost:3306', # host_ip,
    'reskima_db' # db_name,
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
Base.query = session.query_property()


class User(Base):
    __tablename__ = 'users'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))
    email = Column('email', String(100))
    created_at = Column('created_at', Timestamp, server_default=current_timestamp())
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    password = Column('password', String(50))


class Group(Base):
    __tablename__ = 'groups'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', Integer, primary_key=True)
    lat = Column('lat', Float)
    lon = Column('lon', Float)
    address = Column('address', String(100))
    query = Column('query', String(100))
    genre = Column('genre', String(50))
    open_day = Column('open_day', Date)
    open_hour = Column('open_hour', Time)
    max_price = Column('max_price', Integer)
    min_price = Column('min_price', Integer)
    group_price = Column('group_price', Integer)
    group_distance = Column('group_distance', Float)
    created_at = Column('created_at', Timestamp, server_default=current_timestamp())
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    password = Column('password', String(50))


class Restaurants(Base):
    __tablename__ = 'restaurants'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    id = Column('id', Integer, primary_key=True)
    images = Column('images', String(100))
    price = Column('price', Integer)
    open_hour = Column('open_hour', Integer)
    address = Column('address', String(100))
    menu = Column('menu', String(100))
    created_at = Column('created_at', Timestamp, server_default=current_timestamp())
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    password = Column('password', String(50))


class Belongs(Base):
    __tablename__ = 'belongs'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    user = Column('user', Integer, primary_key=True)
    group = Column('group', Integer, primary_key=True)
    request_count = Column('request_count', Integer, nullable=False, server_default='0')
    request_restaurants_num = Column('request_restaurants_num', Integer, nullable=False, server_default='0')
    created_at = Column('created_at', Timestamp, server_default=current_timestamp())
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class History(Base):
    __tablename__ = 'histories'
    __table_args__=({"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"})
    user = Column('user', Integer, primary_key=True)
    group = Column('group', Integer, primary_key=True)
    restaurant = Column('restaurant', Integer, primary_key=True)
    feeling = Column('feeling', Boolean)
    created_at = Column('created_at', Timestamp, server_default=current_timestamp())
    updated_at = Column('update_at', Timestamp, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
