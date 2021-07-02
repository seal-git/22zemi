# from sqlalchemy import *
from flask import jsonify, make_response, request
from app import app_, db_
from app import recommend, api_functions
import mysql.connector
from random import randint
import os
import json
import random
from werkzeug.exceptions import NotFound,BadRequest,InternalServerError
import datetime
import string
import qrcode
from PIL import Image
import base64
from io import BytesIO

"""
mysqlサーバーとの接続はmysql.connectorで行っているが，SQLAlchemyへ換装したい．
"""

'''
現在アプリを使っているグループやユーザを格納する
{group_id1: {
    'Coordinates': (lat,lon),
    'Address': 住所,
    'FilterParams': {}
    'Users': { 'user_id1: {
        'RequestCount': 0,
        'Feeling': {restaurant_id1: true, ... },
        'UnanimousNoticed': [restaurant_id1, ... ]
    }, ... },
    'Restaurants': {restaurant_id1, {'Like': [user_id1, ...], 'All': [user_id1, ...]}, ... },
    'Unanimous': [restaurant_id1, ... ]
}, ... }
'''
current_group = {}

# mysqlサーバーと接続
conn = mysql.connector.connect(
    host = 'mysql', #docker-compose.ymlで指定したコンテナ名
    port = 3306,
    user = 'root',
    password = os.environ['MYSQL_ROOT_PASSWORD'],
    database = 'sample_db'
)

# mysqlサーバーとの接続を確認
conn.ping(reconnect=True)
if conn.is_connected():
    print("db connected!")

def generate_group_id():
    '''
    重複しないグループIDを生成する
    
    Returns
    ----------------
    group_id : string
    '''
    global current_group
    for i in range(1000000):
        group_id = str(randint(0, 999999))
        if group_id not in current_group:
            return group_id
    return group_id

def get_group_id(user_id):
    global current_group
    '''
    ユーザIDからグループIDを得る。グループIDを指定しない場合にはこの関数を使う。グループIDを指定する場合はユーザIDに重複があっても良いが、グループIDを指定しない場合にはユーザIDに重複があってはいけない。
    
    Parameters
    ----------------
    user_id : string
    
    Returns
    ----------------
    group_id : string
    '''
    for gid,g in current_group.items():
        if user_id in g['Users'].keys():
            return gid
    return None

def generate_user_id():
    '''
    重複しないユーザIDを生成する
    
    Returns
    ----------------
    user_id : string
    '''
    global current_group
    for i in range(1000000):
        user_id = ''.join([random.choice(string.ascii_letters + string.digits) for j in range(12)])
        for g in current_group.values():
            for u in g['Users'].items():
                if u == user_id:
                    user_id = ""
        if user_id != "":
            return user_id
    return user_id

def set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice):
    '''
    検索条件を受け取り、current_groupを更新する。
    '''
    global current_group
    if place is None and genre is None and query is None and open_hour is None and maxprice is None and minprice is None: return
    
    if place is not None:
        lat,lon,address = api_functions.get_lat_lon(place)
        current_group[group_id]['Coordinates'] = (lat,lon)
        current_group[group_id]['Address'] = address
    if genre is not None or query is not None:
        if genre is None:
            current_group[group_id]['FilterParams']['query'] = query
        elif query is None:
            current_group[group_id]['FilterParams']['query'] = genre
        else:
            current_group[group_id]['FilterParams']['query'] = genre + ' ' + query
    if open_hour is not None:
        if open_day is not None:
            current_group[group_id]['FilterParams']['open'] = open_day + ',' + open_hour
        else:
            current_group[group_id]['FilterParams']['open'] = str(datetime.datetime.now().day) + ',' + open_hour
    if maxprice is not None:
        current_group[group_id]['FilterParams']['maxprice'] = int(maxprice)
    if minprice is not None:
        current_group[group_id]['FilterParams']['minprice'] = int(minprice)

def get_restaurant_info(group, restaurant_ids):
    '''
    Yahoo local search APIで情報を取得し、json形式で情報を返す
    
    Parameters
    ----------------
    group : dict
       current_group[group_id]
    restaurant_ids : [string]
        restaurant_idのリスト
    
    Returns
    ----------------
    restaurant_info : string
        レスポンスするレストラン情報をjson形式で返す。
    '''
    restaurant_ids_del_None = [x for x in restaurant_ids if x]
    local_search_params = { 'uid': ','.join(restaurant_ids_del_None) }
    
    local_search_json, result_json = api_functions.get_restaurant_info_from_local_search_params(group, local_search_params)
    return result_json


#@app_.after_request
# CORS対策で追記したがうまく働いていない？
# def after_request(response):
#     print("after request is running")
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     return response

@app_.route('/get_sample_db', methods=['POST'])
# ランダムにsample_db.sample_tableから一つ取得
def get_sample_db():
    conn.ping(reconnect=True)  # 接続が途切れた時に再接続する

    cur = conn.cursor(dictionary=True)

    # ランダムに一つ取得
    rand_idx = randint(1, 6)
    sql = ("SELECT * "
           "FROM sample_table "
           f"WHERE user_id={rand_idx}")
    cur.execute(sql)
    content = cur.fetchone()
    result = {
        "keys": list(content.keys()),
        "content": content
    }# JSはオブジェクトのキーの順番を保持しないらしいのでkeyの配列も渡してあげる

    cur.close()
    return make_response(jsonify(result))

@app_.route('/initialize_current_group', methods=['GET','POST'])
# current_groupを初期化
def http_initialize_current_group():
    global current_group
    current_group = {}
    return "current_groupの初期化に成功！"

@app_.route('/init', methods=['GET','POST'])
# まだ使われていないグループIDを返すだけ
def http_init():
    global current_group
    group_id = generate_group_id()
    user_id = generate_user_id()
    result = {'GroupId': group_id, 'UserId': user_id}
    return json.dumps(result, ensure_ascii=False)

@app_.route('/invite', methods=['GET'])
# 検索条件を指定して、招待URLを返す
def http_invite():
    URL = 'https://reskima.com' # TODO: ドメインを取得したら書き換える。

    group_id = request.args.get('group_id')
    # coordinates = data["coordinates"] if data.get("coordinates", False) else None # TODO: デモ以降に実装
    place = request.args.get('place')
    genre = request.args.get("genre")
    query = request.args.get('query')
    open_day = request.args.get('open_day')
    open_hour = request.args.get('open_hour')
    maxprice = request.args.get('maxprice')
    minprice = request.args.get('minprice')
    recommend_method = request.args.get('recommend_method')
    
    group_id = group_id if group_id != None else generate_group_id()
    
    set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice)
    
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
    global current_group
    data = request.get_json()["params"]
    user_id = data["user_id"] if data.get("user_id", False) else None
    group_id = data["group_id"] if data.get("group_id", False) else None
    # coordinates = data["coordinates"] if data.get("coordinates", False) else None # TODO: デモ以降に実装
    place = data["place"] if data.get("place", False) else None
    genre = data["genre"] if data.get("genre", False) else None
    query = data["query"] if data.get("query", False) else None
    open_day = data["open_day"] if data.get("open_day", False) else None
    open_hour = data["open_hour"] if data.get("open_hour", False) else None
    maxprice = data["maxprice"] if data.get("maxprice", False) else None
    minprice = data["minprice"] if data.get("minprice", False) else None
    recommend_method = data["recommend_method"] if data.get("recommend_method", False) else None

    group_id = group_id if group_id != None else get_group_id(user_id)

    # Yahoo本社の住所 # TODO
    address = "東京都千代田区紀尾井町1-3 東京ガ-デンテラス紀尾井町 紀尾井タワ-"
    lat,lon,address = api_functions.get_lat_lon(address)
    # TODO: 開発用に時間を固定
    open_hour = '18'
    
    if group_id not in current_group:
        current_group[group_id] = {'Coordinates': (lat,lon), 'Address': address, 'FilterParams': {}, 'Users': {}, 'Restaurants': {}}
    if user_id not in current_group[group_id]['Users']:
        current_group[group_id]['Users'][user_id] = {'RequestCount': 0, 'Feeling': {}} # 1回目のリクエストは、ユーザを登録する
    else:
        current_group[group_id]['Users'][user_id]['RequestCount'] += 1 # 2回目以降のリクエストは、前回の続きの店舗情報を送る

    # 検索条件
    set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice)

    return recommend.recommend_main(current_group, group_id, user_id, recommend_method)

@app_.route('/feeling', methods=['GET','POST'])
# キープ・リジェクトの結果を受け取り、メモリに格納する。全会一致の店舗を知らせる。
def http_feeling():
    global current_group
    data = request.get_json()["params"]
    user_id = data["user_id"] if data.get("user_id", False) else None
    group_id = data["group_id"] if data.get("group_id", False) else None
    restaurant_id = data["restaurant_id"] if data.get("restaurant_id", False) else None
    feeling = data["feeling"] if data.get("feeling", False) else None

    group_id = group_id if group_id != None else get_group_id(user_id)
    
    # 情報を登録
    current_group[group_id]['Users'][user_id]['Feeling'][restaurant_id] = feeling
    if feeling:
        current_group[group_id]['Restaurants'][restaurant_id]['Like'].add(user_id)
    else:
        current_group[group_id]['Restaurants'][restaurant_id]['Like'].discard(user_id)
    current_group[group_id]['Restaurants'][restaurant_id]['All'].add(user_id)
    
    # 通知の数を返す。全会一致の店の数
    return str(sum([1 for r in current_group[group_id]['Restaurants'].keys() if len(current_group[group_id]["Restaurants"][r]['Like']) >= len(current_group[group_id]['Users'])]))

@app_.route('/popular_list', methods=['GET','POST'])
# 得票数の一番多い店舗のリストを返す。1人のときはキープした店舗のリストを返す。

def http_popular_list():
    data = request.get_json()["params"]
    user_id = data["user_id"] if data.get("user_id", False) else None
    group_id = data["group_id"] if data.get("group_id", False) else None
    group_id = group_id if group_id != None else get_group_id(user_id)
    
    if sum([len(r['All']) for rid,r in current_group[group_id]['Restaurants'].items()]) == 0:
    # if len(current_group[group_id]['Restaurants']) == 0:
        return '[]'

    popular_max = max([r['Like'] for r in current_group[group_id]['Restaurants'].values()])
    restaurant_ids = [rid for rid,r in current_group[group_id]['Restaurants'].items() if r['Like'] == popular_max]
    result_json = get_restaurant_info(current_group[group_id], restaurant_ids)
    return json.dumps(result_json, ensure_ascii=False)

@app_.route('/list', methods=['GET','POST'])
# 得票数が多い順の店舗リストを返す。1人のときはキープした店舗のリストを返す。
def http_list():
    global current_group
    data = request.get_json()["params"]
    user_id = data["user_id"] if data.get("user_id", False) else None
    group_id = data["group_id"] if data.get("group_id", False) else None
    group_id = group_id if group_id != None else get_group_id(user_id)
    
    # ひとりの時はLIKEしたリスト。リジェクトしたら一生お別れ
    if len(current_group[group_id]['Users']) <= 1:
        return http_popular_list()

    restaurant_ids = list(current_group[group_id]['Users'][user_id]['Feeling'].keys())
    result_json = get_restaurant_info(current_group[group_id], restaurant_ids)
    
    # 得票数が多い順に並べる
    result_json.sort(key=lambda x:x['VotesAll']) # 得票数とオススメ度が同じなら、リジェクトが少ない順
    result_json.sort(key=lambda x:x['RecommendLevel'], reverse=True) # 得票数が同じなら、オススメ度順
    result_json.sort(key=lambda x:x['VotesLike'], reverse=True) # 得票数が多い順
    
    return json.dumps(result_json, ensure_ascii=False)

@app_.route('/history', methods=['GET','POST'])
# ユーザに表示した店舗履のリストを返す。履歴。
def http_history():
    global current_group
    data = request.get_json()["params"]
    user_id = data["user_id"] if data.get("user_id", False) else None
    group_id = data["group_id"] if data.get("group_id", False) else None

    group_id = group_id if group_id != None else get_group_id(user_id)

    restaurant_ids = list(current_group[group_id]['Users'][user_id]['Feeling'].keys())
    result_json = get_restaurant_info(current_group[group_id], restaurant_ids)
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
