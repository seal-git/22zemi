# from sqlalchemy import *
from flask import jsonify, make_response, request
from app import app_, db_
from app import recommend, api_functions
import mysql.connector
from random import randint
import os
import json
import random
import datetime

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

def get_group_id(user_id):
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
    local_search_params = { 'uid': ','.join(restaurant_ids) }
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

@app_.route('/init', methods=['GET','POST'])
# まだ使われていないグループIDを返すだけ
def http_init():
    for i in range(1000000):
        group_id = str(randint(0, 999999))
        if group_id not in current_group:
            return group_id

@app_.route('/info', methods=['GET','POST'])
# 店情報を要求するリクエスト
def http_info():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    # coordinates = request.args.get('coordinates') # 位置情報
    place = request.args.get('place') # 場所
    genre = request.args.get('genre') # ジャンル
    query = request.args.get('query') # 場所やジャンルなどの検索窓入力
    open_day = request.args.get('open_day') # 
    open_hour = request.args.get('open_hour') # 時間
    maxprice = request.args.get('maxprice') # 最高値
    minprice = request.args.get('minprice') # 最安値
    recommend_method = request.args.get('recommend')
    
    group_id = group_id if group_id != None else get_group_id(user_id)

    # Yahoo本社の住所
    address = "東京都千代田区紀尾井町1-3 東京ガ-デンテラス紀尾井町 紀尾井タワ-"
    lat,lon,address = api_functions.get_lat_lon(address)
    
    if group_id not in current_group:
        current_group[group_id] = {'Coordinates': (lat,lon), 'Address': address, 'FilterParams': {}, 'Users': {}, 'Restaurants': {}}
    if user_id not in current_group[group_id]['Users']:
        current_group[group_id]['Users'][user_id] = {'RequestCount': 0, 'Feeling': {}} # 1回目のリクエストは、ユーザを登録する
    else:
        current_group[group_id]['Users'][user_id]['RequestCount'] += 1 # 2回目以降のリクエストは、前回の続きの店舗情報を送る

    # 検索条件
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
            current_group[group_id]['FilterParams']['query'] = query + ' ' + query
    if open_hour is not None:
        if open_day is not None:
            current_group[group_id]['FilterParams']['open'] = open_day + ',' + open_hour
        else:
            current_group[group_id]['FilterParams']['open'] = str(datetime.datetime.now().day) + ',' + open_hour
    if maxprice is not None:
        current_group[group_id]['FilterParams']['maxprice'] = int(maxprice)
    if minprice is not None:
        current_group[group_id]['FilterParams']['minprice'] = int(minprice)

    return recommend.recommend_main(current_group, group_id, user_id, recommend_method)

@app_.route('/feeling', methods=['GET','POST'])
# キープ・リジェクトの結果を受け取り、メモリに格納する。全会一致の店舗を知らせる。
def http_feeling():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    restaurant_id = request.args.get('restaurant_id')
    feeling = request.args.get('feeling')
    group_id = group_id if group_id != None else get_group_id(user_id)
    
    # 情報を登録
    current_group[group_id]['Users'][user_id]['Feeling'][restaurant_id] = feeling
    if restaurant_id not in current_group[group_id]['Restaurants']:
        current_group[group_id]['Restaurants'][restaurant_id] = {'Like': set(), 'All': set()}
    if feeling:
        current_group[group_id]['Restaurants'][restaurant_id]['Like'].add(user_id)
    else:
        current_group[group_id]['Restaurants'][restaurant_id]['Like'].discard(user_id)
    current_group[group_id]['Restaurants'][restaurant_id]['All'].add(user_id)
    
    # 通知の数を返す。全会一致の店の数
    return str(sum([1 for r in current_group[group_id]['Restaurants'].values() if len(r['Like']) >= len(current_group[group_id]['Users'])]))

@app_.route('/popular_list', methods=['GET','POST'])
# 得票数の一番多い店舗のリストを返す。1人のときはキープした店舗のリストを返す。
def http_popular_list():
    group_id = request.args.get('group_id')
    group_id = group_id if group_id != None else get_group_id(request.args.get('user_id'))

    if len(current_group[group_id]['Restaurants']) == 0:
        return '[]'

    popular_max = max([r['Like'] for r in current_group[group_id]['Restaurants'].values()])
    restaurant_ids = [rid for rid,r in current_group[group_id]['Restaurants'].items() if r['Like'] == popular_max]
    result_json = get_restaurant_info(current_group[group_id], restaurant_ids)
    return json.dumps(result_json, ensure_ascii=False)

@app_.route('/list', methods=['GET','POST'])
# 得票数が多い順の店舗リストを返す。1人のときはキープした店舗のリストを返す。
def http_list():
    group_id = request.args.get('group_id')
    group_id = group_id if group_id != None else get_group_id(request.args.get('user_id'))
    
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
    group_id = request.args.get('group_id')
    user_id = request.args.get('user_id')
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
