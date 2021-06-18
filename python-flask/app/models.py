# from sqlalchemy import *
from flask import jsonify, make_response, request
from app import app_, db_
from app import api_functions
import mysql.connector
from random import randint
import os
#from app.api_functions import get_restaurant_info_from_local_search_params

"""
mysqlサーバーとの接続はmysql.connectorで行っているが，SQLAlchemyへ換装したい．
"""


# 現在アプリを使っているグループやユーザを格納する
current_group = {} # {group_id1: {'Coordinates': (lat,lon), 'Users': { 'user_id1: {'RequestCount': 0, 'Feeling': {restaurant_id1: true, ... }}, ... }, 'Unanimous': [restaurant_id1, ... ]}, ... }


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


# Yahoo local search APIで情報を取得し、json形式で情報を返す
# @param coordinates : (int, int) : (緯度, 経度)のタプル
# @param request_count : int : 何回目のリクエストかを指定する。回数に応じて別の店舗を返す。同じ値を指定したら同じ結果が返るはず。
# @return : string : json形式
def search_restaurant_info(coordinates, request_count):
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


@app_.route('/info')
# 店情報を要求するリクエスト
def http_info():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    # coordinates = request.args.get('coordinates') # 位置情報
    
    # Yahoo本社の座標を決め打ち
    lat = 35.68001 # 緯度
    lon = 139.73284 # 経度
    
    if group_id not in current_group:
        current_group[group_id] = {'Coordinates': (lat,lon), 'Users': {}, 'Unanimous': []}
    if user_id not in current_group[group_id]['Users']:
        current_group[group_id]['Users'][user_id] = {'RequestCount': 0, 'Feeling': {}} # 1回目のリクエストは、ユーザを登録する
    else:
        current_group[group_id]['Users'][user_id]['RequestCount'] += 1 # 2回目以降のリクエストは、前回の続きの店舗情報を送る

    return search_restaurant_info(current_group[group_id]['Coordinates'], current_group[group_id]['Users'][user_id]['RequestCount'])

@app_.route('/feeling')
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
    
    # 全員一致だったらcurrent_groupに格納する
    if feeling and all([ u['Feeling'][restaurant_id] for u in current_group[group_id]['Users'].values() ]):
        current_group[group_id]['Unanimous'].append( restaurant_id )
    
    # 全会一致の店舗を知らせる
    local_search_params = { 'uid': ','.join(current_group[group_id]['Unanimous']) }
    return api_functions.get_restaurant_info_from_local_search_params(current_group[group_id]['Coordinates'], local_search_params)


