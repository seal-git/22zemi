# from sqlalchemy import *
from flask import jsonify, make_response, request
from app import app_, db_
from app import api_functions
import mysql.connector
from random import randint
import os
import json

"""
mysqlサーバーとの接続はmysql.connectorで行っているが，SQLAlchemyへ換装したい．
"""

# 現在アプリを使っているグループやユーザを格納する
current_group = {} # {group_id1: {'Coordinates': (lat,lon), 'Users': { 'user_id1: {'RequestCount': 0, 'Feeling': {restaurant_id1: true, ... }, 'UnanimousNoticed': [restaurant_id1, ... ]}, ... }, 'Unanimous': [restaurant_id1, ... ]}, ... }

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

def search_restaurant_info(coordinates, request_count):
    '''
    Yahoo local search APIで情報を検索し、json形式で情報を返す
    
    Parameters
    ----------------
    coordinates : (int, int)
        (緯度, 経度)のタプル
    request_count : int
        何回目のリクエストかを指定する。回数に応じて別の店舗を返す。同じ値を指定したら同じ結果が返るはず。
    
    Returns
    ----------------
    restaurant_info : string
        レスポンスするレストラン情報をjson形式で返す。
    '''
    RESULTS_COUNT = 25 # 一回に取得する店舗の数
    
     # YahooローカルサーチAPIで検索するクエリ
    local_search_params = {
        # 中心地から1km以内のグルメを検索
        'lat': coordinates[0], # 緯度
        'lon': coordinates[1], # 経度
        'dist': 3, # 中心地点からの距離 # 最大20km
        'gc': '01', # グルメ
        'image': True, # 画像がある店
        'open': 'now', # 現在開店している店舗
        'sort': 'hybrid', # 評価や距離などを総合してソート
        'start': RESULTS_COUNT * request_count, # 表示範囲：開始位置
        'results': RESULTS_COUNT # 表示範囲：店舗数
    }

    # Yahoo local search APIで店舗情報を取得
    return api_functions.get_restaurant_info_from_local_search_params(coordinates, local_search_params)

def get_restaurant_info(coordinates, restaurant_ids):
    '''
    Yahoo local search APIで情報を取得し、json形式で情報を返す
    
    Parameters
    ----------------
    coordinates : (int, int)
        (緯度, 経度)のタプル
    restaurant_ids : [string]
        restaurant_idのリスト
    
    Returns
    ----------------
    restaurant_info : string
        レスポンスするレストラン情報をjson形式で返す。
    '''
    local_search_params = { 'uid': ','.join(restaurant_ids) }
    return api_functions.get_restaurant_info_from_local_search_params(coordinates, local_search_params)

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

@app_.route('/info', methods=['GET','POST'])
# 店情報を要求するリクエスト
def http_info():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    # coordinates = request.args.get('coordinates') # 位置情報
    
    # Yahoo本社の座標を決め打ち
    lat = 35.68001 # 緯度
    lon = 139.73284 # 経度
    
    if group_id not in current_group:
        current_group[group_id] = {'Coordinates': (lat,lon), 'Users': {}, 'Unanimous': set()}
    if user_id not in current_group[group_id]['Users']:
        current_group[group_id]['Users'][user_id] = {'RequestCount': 0, 'Feeling': {}, 'UnanimousNoticed': set()} # 1回目のリクエストは、ユーザを登録する
    else:
        current_group[group_id]['Users'][user_id]['RequestCount'] += 1 # 2回目以降のリクエストは、前回の続きの店舗情報を送る

    return search_restaurant_info(current_group[group_id]['Coordinates'], current_group[group_id]['Users'][user_id]['RequestCount'])

@app_.route('/feeling', methods=['GET','POST'])
# キープ・リジェクトの結果を受け取り、メモリに格納する。全会一致の店舗を知らせる。
def http_feeling():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    restaurant_id = request.args.get('restaurant_id')
    feeling = request.args.get('feeling')
    
    current_group[group_id]['Users'][user_id]['Feeling'][restaurant_id] = feeling
    
    # 全会一致だったのをリジェクトしたら全会一致リストから消す
    if not feeling and restaurant_id in current_group[group_id]['Unanimous']:
        current_group[group_id]['Unanimous'].remove(restaurant_id)
        for u in current_group[group_id]['Users'].values():
            if restaurant_id in u['UnanimousNoticed']:
                u['UnanimousNoticed'].remove(restaurant_id)
    
    # 全員一致だったらcurrent_groupに格納する
    if feeling and all([ u['Feeling'].get(restaurant_id) for u in current_group[group_id]['Users'].values() ]):
        current_group[group_id]['Unanimous'].add( restaurant_id )
    
    # ふたり以上だったら全会一致の店舗のうち、まだ知らせていないものを知らせる
    if len(current_group[group_id]['Users']) >= 2 :
        new_unanimous = current_group[group_id]['Unanimous'] - current_group[group_id]['Users'][user_id]['UnanimousNoticed']
        current_group[group_id]['Users'][user_id]['UnanimousNoticed'] |= new_unanimous
        local_search_params = { 'uid': ','.join(list(new_unanimous)) }
        return api_functions.get_restaurant_info_from_local_search_params(current_group[group_id]['Coordinates'], local_search_params)
    else:
        return '[]'

@app_.route('/popular', methods=['GET','POST'])
# 得票数の多い店舗のリストを返す。1人のときはキープした店舗のリストを返す。
def http_popular():
    group_id = request.args.get('group_id')

    restaurant_popular = {}
    for u in current_group[group_id]['Users'].values():
        for restaurant_id, feeling in u['Feeling'].items():
            if restaurant_id not in restaurant_popular:
                restaurant_popular[restaurant_id] = 1
            else:
                restaurant_popular[restaurant_id] += 1

    if len(restaurant_popular) == 0:
        return '[]'

    popular_max = max( restaurant_popular.values() )
    restaurant_ids = [rid for rid,pop in restaurant_popular.items() if pop == popular_max]
    return get_restaurant_info(current_group[group_id]['Coordinates'], restaurant_ids)

@app_.route('/history', methods=['GET','POST'])
# ユーザに表示した店舗履のリストを返す。履歴。
def http_history():
    group_id = request.args.get('group_id')
    user_id = request.args.get('user_id')

    restaurant_ids = list(current_group[group_id]['Users'][user_id]['Feeling'].keys())
    return get_restaurant_info(current_group[group_id]['Coordinates'], restaurant_ids)

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
