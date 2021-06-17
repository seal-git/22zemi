# from sqlalchemy import *
from flask import jsonify, make_response, request
from app import app_, db_
import mysql.connector
from random import randint
import os
import urllib.request
import json
from geopy.distance import great_circle

"""
mysqlサーバーとの接続はmysql.connectorで行っているが，SQLAlchemyへ換装したい．
"""


# mysqlを使う代わりにとりあえず変数作った
temp_db = {} # {group_id1: {'Coordinates': (lat,lon), 'Users': { 'user_id1: {'RequestCount': 0, 'Feeling': {restaurant_id1: true, ... }}, ... }}, ... }


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
# @param coordinates : (int, int) (緯度, 経度)のタプル
# @param request_count : int 何回目のリクエストかを指定する。回数に応じて別の店舗を返す。同じ値を指定したら同じ結果が返るはず。
def get_info_from_yahoo_local_search(coordinates, request_count):
    MAX_LIST_COUNT = 10
    RESULTS_COUNT = 25 # 一回に取得する店舗の数
    
    lunch_or_dinner = 'dinner' # 価格表示に使用。今のところ検索には使用していない

    #  ヤフー本社から1km以内のグルメを検索
    local_search_query = {} # YahooローカルサーチAPIで検索するクエリ
    local_search_query['appid'] = os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID']
        # 検索条件↓
    local_search_query['lat'] = coordinates[0] # 緯度
    local_search_query['lon'] = coordinates[1] # 経度
    local_search_query['dist'] = 3 # 中心地点からの距離 # 最大20km
    local_search_query['gc'] = '01' # グルメ
    local_search_query['image'] = True # 画像がある店
    local_search_query['open'] = 'now' # 現在開店している店舗
    local_search_query['sort'] = 'hybrid' # 評価や距離などを総合してソート
        # 表示方法↓
    local_search_query['output'] = 'json' #
    local_search_query['detail'] = 'full' #
    local_search_query['start'] = RESULTS_COUNT * request_count #
    local_search_query['results'] = RESULTS_COUNT #

    # Yahoo local search APIで店舗情報を取得
    with urllib.request.urlopen('https://map.yahooapis.jp/search/local/V1/localSearch?' + urllib.parse.urlencode(local_search_query)) as response:
        local_search_json = json.loads(response.read())

    # 検索の該当が無かったとき
    if local_search_json['ResultInfo']['Count'] == 0:
        return "{}"
    
    # 店舗情報をjson形式で返す
    result_json = []
    for i,feature in enumerate(local_search_json['Feature']):
        result_json.append({})
        result_json[i]['Restaurant_id'] = feature['Property']['Uid']
        result_json[i]['Name'] = feature['Name']
        result_json[i]['Distance'] = great_circle(coordinates, tuple(reversed([float(x) for x in feature['Geometry']['Coordinates'].split(',')]))).m # 緯度・経度から距離を計算
        result_json[i]['CatchCopy'] = feature['Property'].get('CatchCopy')
        result_json[i]['Price'] = feature['Property']['Detail']['LunchPrice'] if lunch_or_dinner == 'lunch' and feature['Property']['Detail']['LunchFlag'] == true else feature['Property']['Detail'].get('DinnerPrice')
        result_json[i]['Image'] = [feature['Property']['Detail']['Image'+str(j)] for j in range(MAX_LIST_COUNT) if 'Image'+str(j) in feature['Property']['Detail']] # Image1, Image2 ... のキーをリストに。
        result_json[i]['LeadImage'] = feature['Property'].get('LeadImage')
        result_json[i]['CassetteOwnerLogoImage'] = feature['Property']['Detail'].get('CassetteOwnerLogoImage')
        result_json[i]['PersistencyImage'] = [feature['Property']['Detail']['PersistencyImage'+str(j)] for j in range(MAX_LIST_COUNT) if 'PersistencyImage'+str(j) in feature['Property']['Detail']] # PersistencyImage1, PersistencyImage2 ... のキーをリストに。
        result_json[i]['TopRankItem'] = [feature['Property']['Detail']['TopRankItem'+str(j)] for j in range(MAX_LIST_COUNT) if 'TopRankItem'+str(j) in feature['Property']['Detail']] # TopRankItem1, TopRankItem2 ... のキーをリストに。

    return json.dumps(result_json)


@app_.after_request
# CORS対策で追記したがうまく働いていない？
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


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


@app_.route('/init')
# 最初にリクエストするやつ
def get_init():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    location = request.args.get('location')
    
    # Yahoo本社の座標を決め打ち
    lat = 35.68001 # 緯度
    lon = 139.73284 # 経度
    
    if group_id not in temp_db:
        temp_db[group_id] = {'Coordinates': (lat,lon), 'Users': {}}
    if user_id not in temp_db[group_id]['Users']:
        temp_db[group_id]['Users'][user_id] = {'RequestCount': 0, 'Feeling': {}}


    return get_info_from_yahoo_local_search(temp_db[group_id]['Coordinates'], temp_db[group_id]['Users'][user_id]['RequestCount'])


@app_.route('/more')
# 2回目以降、さらに店舗を検索する
def get_more():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    
    temp_db[group_id]['Users'][user_id]['RequestCount'] += 1

    return get_info_from_yahoo_local_search(temp_db[group_id]['Coordinates'], temp_db[group_id]['Users'][user_id]['RequestCount'])


@app_.route('/feeling')
# キープ・リジェクトの結果を受け取る。メモリに格納
def post_feeling():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    restaurant_id = request.args.get('restaurant_id')
    feeling = request.args.get('feeling')
    
    temp_db[group_id]['Users'][user_id]['Feeling'][restaurant_id] = feeling

    return ""


