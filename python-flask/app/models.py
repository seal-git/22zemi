# from sqlalchemy import *
from flask import jsonify, make_response, request
from app import app_, db_
from app import recommend, api_functions
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History
import mysql.connector
from random import randint
import json
import random
from werkzeug.exceptions import NotFound,BadRequest,InternalServerError
import datetime
import string
import qrcode
from PIL import Image
import base64
from io import BytesIO
import time
import sqlalchemy
from sqlalchemy.sql.functions import current_timestamp



# # mysqlサーバーと接続
# conn = mysql.connector.connect(
#     host = 'mysql', #docker-compose.ymlで指定したコンテナ名
#     port = 3306,
#     user = 'root',
#     password = os.environ['MYSQL_ROOT_PASSWORD'],
#     database = 'sample_db'
# )

# # mysqlサーバーとの接続を確認
# conn.ping(reconnect=True)
# if conn.is_connected():
#     print("db connected!")

# #@app_.after_request
# # CORS対策で追記したがうまく働いていない？
# # def after_request(response):
# #     print("after request is running")
# #     response.headers.add('Access-Control-Allow-Origin', '*')
# #     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
# #     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
# #     return response

# @app_.route('/get_sample_db', methods=['POST'])
# # ランダムにsample_db.sample_tableから一つ取得
# def get_sample_db():
#     conn.ping(reconnect=True)  # 接続が途切れた時に再接続する

#     cur = conn.cursor(dictionary=True)

#     # ランダムに一つ取得
#     rand_idx = randint(1, 6)
#     sql = ("SELECT * "
#            "FROM sample_table "
#            f"WHERE user_id={rand_idx}")
#     cur.execute(sql)
#     content = cur.fetchone()
#     result = {
#         "keys": list(content.keys()),
#         "content": content
#     }# JSはオブジェクトのキーの順番を保持しないらしいのでkeyの配列も渡してあげる

#     cur.close()
#     return make_response(jsonify(result))


def generate_group_id():
    '''
    重複しないグループIDを生成する
    
    Returns
    ----------------
    group_id : int
    '''
    for i in range(1000000):
        group_id = randint(0, 999999)
        fetch = session.query(Group).filter(Group.id==group_id).first()
        if fetch is None:
            return group_id
    return group_id # error


def get_group_id(user_id):
    '''
    ユーザIDからグループIDを得る。グループIDを指定しない場合にはこの関数を使う。グループIDを指定する場合はユーザIDに重複があっても良いが、グループIDを指定しない場合にはユーザIDに重複があってはいけない。
    
    Parameters
    ----------------
    user_id : int
    
    Returns
    ----------------
    group_id : int
    '''
    fetch_belong = session.query(Belong.group).filter(Belong.user==user_id).first()
    if fetch_belong is not None:
        return fetch_belong.group
    else:
        return None # error


def generate_user_id():
    '''
    重複しないユーザIDを生成する
    
    Returns
    ----------------
    user_id : int
    '''
    for i in range(1000000):
        user_id = randint(0, 999999) # ''.join([random.choice(string.ascii_letters + string.digits) for j in range(12)])
        fetch = session.query(User).filter(User.id==user_id).first()
        if fetch is None:
            return user_id
    return user_id # error


def set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice):
    '''
    検索条件を受け取り、dbを更新する。
    '''
    if place is None and genre is None and query is None and open_hour is None and maxprice is None and minprice is None: return
    
    fetch_group = session.query(Group).filter(Group.id==group_id).first()

    if place is not None:
        lat,lon,address = api_functions.get_lat_lon_address(place)
        fetch_group.lat = lat
        fetch_group.lon = lon
        fetch_group.address = address
    fetch_group.query = query
    fetch_group.genre = genre
    fetch_group.max_price = maxprice
    fetch_group.min_price = minprice
    if open_hour is not None:
        if open_day is not None:
            fetch_group.open_day = open_day
        else:
            fetch_group.open_day = datetime.datetime.strftime( datetime.date.today() if datetime.datetime.now().hour<=int(open_hour) else datetime.date.today() + datetime.timedelta(days=1), '%Y-%m-%d')
    else:
        fetch_group.open_day = current_timestamp()
    fetch_group.open_hour = open_hour if open_hour is not None else current_timestamp()

    session.commit()


@app_.route('/initialize_current_group', methods=['GET','POST'])
# dbを初期化
def http_initialize_current_group():
    Base.metadata.create_all(bind=ENGINE)
    return "complete create_db\n"


@app_.route('/init', methods=['GET','POST'])
# まだ使われていないグループIDを返す
def http_init():
    group_id = generate_group_id()
    user_id = generate_user_id()
    result = {'GroupId': str(group_id), 'UserId': str(user_id)}
    return json.dumps(result, ensure_ascii=False)


@app_.route('/invite', methods=['GET', 'POST'])
# 検索条件を指定して、招待URLを返す
def http_invite():
    URL = 'https://reskima.com'
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    # coordinates = data["coordinates"] if data.get("coordinates", False) else None # TODO: デモ以降に実装
    place = data["place"] if data.get("place", False) else None
    genre = data["genre"] if data.get("genre", False) else None
    query = data["query"] if data.get("query", False) else None
    open_day = data["open_day"] if data.get("open_day", False) else None
    open_hour = data["open_hour"] if data.get("open_hour", False) else None
    maxprice = data["maxprice"] if data.get("maxprice", False) else None
    minprice = data["minprice"] if data.get("minprice", False) else None
    recommend_method = data["recommend_method"] if data.get("recommend_method", False) else None
    
    group_id = group_id if group_id is not None else generate_group_id()
    
    set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice)
    
    # QRコードを作って返す
    invite_url = URL + '?group_id=' + str(group_id)
    qr_img = qrcode.make(invite_url)
    buf = BytesIO()
    qr_img.save(buf, format="jpeg")
    qr_img_base64 = base64.b64encode(buf.getvalue()).decode("ascii")
    result = {'GroupId': group_id, 'UserId': generate_user_id(), 'Url': invite_url, 'Qr': qr_img_base64}
    return json.dumps(result, ensure_ascii=False)


@app_.route('/info', methods=['GET','POST'])
# 店情報を要求するリクエスト
def http_info():
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    # coordinates = data["coordinates"] if data.get("coordinates", False) else one # TODO: デモ以降に実装
    place = data["place"] if data.get("place", False) else None
    genre = data["genre"] if data.get("genre", False) else None
    query = data["query"] if data.get("query", False) else None
    open_day = data["open_day"] if data.get("open_day", False) else None
    open_hour = data["open_hour"] if data.get("open_hour", False) else None
    maxprice = data["maxprice"] if data.get("maxprice", False) else None
    minprice = data["minprice"] if data.get("minprice", False) else None
    recommend_method = data["recommend_method"] if data.get("recommend_method", False) else None

    group_id = group_id if group_id is not None else get_group_id(user_id)

    # Yahoo本社の住所 # TODO
    address = "東京都千代田区紀尾井町1-3 東京ガ-デンテラス紀尾井町 紀尾井タワ-"
    lat,lon,address = api_functions.get_lat_lon_address(address)
    # TODO: 開発用に時間を固定
    open_hour = '18'
    
    # ユーザが未登録ならばデータベースに登録する
    fetch_user = session.query(User).filter(User.id==user_id).first()
    if fetch_user is None:
        new_user = User()
        new_user.id = user_id
        session.add(new_user)
        session.commit()
    
    # グループが未登録ならばデータベースに登録する
    fetch_group = session.query(Group).filter(Group.id==group_id).first()
    if fetch_group is None:
        new_group = Group()
        new_group.id = group_id
        new_group.lat = lat
        new_group.lon = lon
        new_group.address = address
        new_group.recommend_method = recommend_method
        session.add(new_group)
        session.commit()
        fetch_group = session.query(Group).filter(Group.id==group_id).one()

    # 所属が未登録ならばデータベースに登録する
    fetch_belong = session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).first()
    if fetch_belong is None:
        new_belong = Belong()
        new_belong.user = user_id
        new_belong.group = group_id
        session.add(new_belong)
        session.commit()
        fetch_belong = session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()
    else:
        fetch_belong.request_count += 1
        session.commit()

    # 検索条件
    set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice)
    result_json = recommend.recommend_main(fetch_group, group_id, user_id)
    fetch_belong.request_restaurants_num = len(result_json) + 1
    session.commit()
    return json.dumps(result_json, ensure_ascii=False)


@app_.route('/feeling', methods=['GET','POST'])
# キープ・リジェクトの結果を受け取り、メモリに格納する。全会一致の店舗を知らせる。
def http_feeling():
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    restaurant_id = data["restaurant_id"] if data.get("restaurant_id", False) else None
    feeling = data["feeling"] if data.get("feeling", False) else None

    group_id = group_id if group_id is not None else get_group_id(user_id)
    
    # 履歴にfeelingを登録
    fetch_exist_history = session.query(History).filter(History.group==group_id, History.user==user_id, History.restaurant==restaurant_id).first()
    if fetch_exist_history is not None:
        session.delete(fetch_exist_history)
    new_history = History()
    new_history.group = group_id
    new_history.user = user_id
    new_history.restaurant = restaurant_id
    new_history.feeling = feeling
    session.add(new_history)
    session.commit()

    # 通知の数を返す。全会一致の店の数
    alln = session.query(Belong).filter(Belong.group==group_id).count() # 参加人数
    return str( session.query(sqlalchemy.func.count("*")).filter(History.group==group_id, History.feeling==True).group_by(History.restaurant).having(sqlalchemy.func.count("*")>=alln).count() )


@app_.route('/list', methods=['GET','POST'])
# 得票数が多い順の店舗リストを返す。1人のときはキープした店舗のリストを返す。
# リストのアイテムが存在しない場合はnullを返す
def http_list():
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    group_id = group_id if group_id != None else get_group_id(user_id)

    # レストランごとに投票数をカウント
    fetch_histories = session.query(History.restaurant, sqlalchemy.func.count("*").label("count")).filter(History.group==group_id, History.feeling==True).group_by(History.restaurant).order_by(desc(sqlalchemy.func.count("*"))).all()
    # リストに存在しない時は空のリストを返す
    if len(fetch_histories) == 0:
        return "[]"
    # 表示する店舗を選ぶ．ひとりのときはLIKEした店だけ．2人以上のときはすべて表示．
    alln = session.query(Belong).filter(Belong.group==group_id).count() # 参加人数
    restaurant_ids = [h.restaurant for h in fetch_histories] if alln >= 2 else [h.restaurant for h in fetch_histories if h.count != 0]
    fetch_group = session.query(Group).filter(Group.id==group_id).first()
    result_json = api_functions.get_restaurants_info(fetch_group, group_id, restaurant_ids)

    # 得票数が多い順に並べる
    result_json.sort(key=lambda x:x['VotesAll']) # 得票数とオススメ度が同じなら、リジェクトが少ない順
    result_json.sort(key=lambda x:x['RecommendScore'], reverse=True) # 得票数が同じなら、オススメ度順
    result_json.sort(key=lambda x:x['VotesLike'], reverse=True) # 得票数が多い順

    return json.dumps(result_json, ensure_ascii=False)


@app_.route('/history', methods=['GET','POST'])
# ユーザに表示した店舗履のリストを返す。履歴。
def http_history():
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    group_id = group_id if group_id != None else get_group_id(user_id)

    fetch_histories = session.query(History.restaurant).filter(History.group==group_id).order_by(updated_at).all()
    result_json = api_functions.get_restaurants_info(group_id, [h.restaurant for h in fetch_histories])
    return json.dumps(result_json, ensure_ascii=False)


@app_.route('/decision', methods=['GET','POST'])
# 現状はアクセスのテスト用,最終決定時のURL
def http_decision():
    decision_json = {"decision":"test"}
    return decision_json


@app_.route('/test', methods=['GET','POST'])
# アクセスのテスト用,infoと同じ結果を返す
def http_test():
    test_result_json = [{"Restaurant_id": "a72a5ed2c330467bd4b4b01a0302bdf977ed00df", 
    "Name": "\u30a8\u30af\u30bb\u30eb\u30b7\u30aa\u30fc\u30eb\u3000\u30ab\u30d5\u30a7\u3000\u30db\u30c6\u30eb\u30b5\u30f3\u30eb\u30fc\u30c8\u8d64\u5742\u5e97", # エクセルシオール　カフェ　ホテルサンルート赤坂店
    "Distance": 492.80934328345614, 
    "CatchCopy": "test", 
    "Price": "test", 
    "TopRankItem": [], 
    "CassetteOwnerLogoImage": "https://iwiz-olp.c.yimg.jp/c/olp/6e/6e6c4795b23a5e45540addb5ff6f0d00/info/55/09/logo/logo_doutor.png", 
    "Images": []
    }]

    return json.dumps(test_result_json)


# アクセスエラー処理
@app_.errorhandler(BadRequest)
@app_.errorhandler(NotFound)
@app_.errorhandler(InternalServerError)
def error_handler(e):
    res = jsonify({ 
                     "error": {
                          "name": error.name, 
                          "description": error.description 
                      }
                   })
    return res, e.code

