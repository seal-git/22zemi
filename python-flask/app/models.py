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
temp_db_by_group = {} # {group_id1: {user_id1: {request_count: 0, feeling: {restaurant_id1: true, ... }}, ... }, ... }

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
# @param request_count : int 何回目のリクエストかを指定する。回数に応じて別の店舗を返す。同じ値を指定したら同じ結果が返るはず。
def get_info_from_yahoo_local_search(request_count):
    MAX_LIST_COUNT = 10
    RESULTS_COUNT = 25 # 一回に取得する店舗の数

    #  ヤフー本社から1km以内のグルメを検索
    lat = 35.68001 # 緯度
    lon = 139.73284 # 経度
    dist_max = 3 # 中心地点からの距離 # 最大20km
    lunch_or_dinner = 'dinner'
    # gc=01: グルメ, sort=hybrid: 評価や距離などでソート, image=true: 画像がある店, open=now: 今開店している店, 
    with urllib.request.urlopen('https://map.yahooapis.jp/search/local/V1/localSearch?appid='+os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID']+'&gc=01&lat='+str(lat)+'&lon='+str(lon)+'&dist='+str(dist_max)+'&image=true&open=now&sort=hybrid&output=json&detail=full&start='+str(RESULTS_COUNT*request_count)+'&results='+str(RESULTS_COUNT)) as response:
        local_search_json = json.loads(response.read())
    result_json = []
    for i,feature in enumerate(local_search_json['Feature']):
        result_json.append({})
        result_json[i]['Restaurant_id'] = feature['Property']['Uid']
        result_json[i]['Name'] = feature['Name']
        result_json[i]['Distance'] = great_circle((lat,lon), tuple(reversed([float(x) for x in feature['Geometry']['Coordinates'].split(',')]))).m # 緯度・経度から距離を計算
        result_json[i]['CatchCopy'] = feature['Property'].get('CatchCopy')
        result_json[i]['Price'] = feature['Property']['Detail']['LunchPrice'] if lunch_or_dinner == 'lunch' and feature['Property']['Detail']['LunchFlag'] == true else feature['Property']['Detail'].get('DinnerPrice')
        result_json[i]['Image'] = [feature['Property']['Detail']['Image'+str(j)] for j in range(MAX_LIST_COUNT) if 'Image'+str(j) in feature['Property']['Detail']] # Image1, Image2 ... のキーをリストに。
        result_json[i]['LeadImage'] = feature['Property']['LeadImage']
        result_json[i]['CassetteOwnerLogoImage'] = feature['Property']['Detail']['CassetteOwnerLogoImage']
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
    
    if group_id not in temp_db_by_group:	
        temp_db_by_group[group_id] = {}
    if user_id not in temp_db_by_group[group_id]:
        temp_db_by_group[group_id][user_id] = {'request_count': 0, 'feeling': {}}

    return get_info_from_yahoo_local_search(temp_db_by_group[group_id][user_id]['request_count'])

@app_.route('/more')
# 2回目以降、さらに店舗を検索する
def get_more():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    
    temp_db_by_group[group_id][user_id]['request_count'] += 1

    return get_info_from_yahoo_local_search(temp_db_by_group[group_id][user_id]['request_count'])
    
@app_.route('/feeling')
# キープ・リジェクトの結果を受け取る。メモリに格納
def post_feeling():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    restaurant_id = request.args.get('restaurant_id')
    feeling = request.args.get('feeling')
    
    temp_db_by_group[group_id][user_id]['feeling'][restaurant_id] = feeling

    return ""
    

