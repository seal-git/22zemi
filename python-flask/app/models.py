# from sqlalchemy import *
from flask import jsonify, make_response, request
from app import app_, db_
from app import database_functions, recommend, api_functions
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from random import randint
import json
from werkzeug.exceptions import NotFound,BadRequest,InternalServerError
import qrcode
from PIL import Image
import base64
from io import BytesIO
import time
import requests
from sqlalchemy.sql.functions import current_timestamp
import threading

# SPEED_UP_FLG
#   Trueにすると高速化できるが、レコメンドの反映が遅れる
#   RecommendSimpleなら NEXT_RESPONSE = True , RECOMMEND_PRIORITY = False 。
#   RecommendSVM   なら NEXT_RESPONSE = False, RECOMMEND_PRIORITY = True  。
NEXT_RESPONSE = True
RECOMMEND_PRIORITY = True # RecommendSimpleでTrueにすると死にます

RECOMMEND_METHOD = 'svm'
API_METHOD = 'yahoo'


def get_restaurants_info_from_recommend_priority(fetch_group, group_id, user_id):
    '''
    あらかじめ優先度が計算されていたら、優先度順にレストランを取得する。
    
    Parameters
    ----------------
    fetch_group
    group_id
    user_id
    
    Returns
    ----------------
    restaurnts_info : [dict]
    '''
    histories_restaurants = [h.restaurant for h in session.query(History.restaurant).filter(History.group==group_id, History.user==user_id).all()]
    fetch_votes = session.query(Vote).filter(Vote.group==group_id, Vote.recommend_priority is not None).order_by(Vote.recommend_priority).all()
    restaurants_ids = []
    for fv in fetch_votes:
        if fv.restaurant not in histories_restaurants:
            restaurants_ids.append(fv.restaurant)
            if len(restaurants_ids) == recommend.RESULTS_COUNT:
                return api_functions.get_restaurants_info(fetch_group, group_id, restaurants_ids)
    
    # まだ優先度を計算していない時や，RecommendSimple等で優先度を計算しない時
    fetch_votes = session.query(Vote).filter(Vote.group==group_id, Vote.recommend_priority is None).all()
    for fv in fetch_votes:
        if fv.restaurant not in histories_restaurants:
            restaurants_ids.append(fv.restaurant)
            if len(restaurants_ids) == recommend.RESULTS_COUNT:
                return api_functions.get_restaurants_info(fetch_group, group_id, restaurants_ids)
    
    # ストックしている店舗数が足りない時。最初のリクエスト等。
    return recommend.recommend_main(fetch_group, group_id, user_id)


def create_response_from_restaurants_info(restaurants_info):
    '''
    レスポンスを生成する仕上げ
    '''

    IMAGE_DIRECTORY_PATH = './data/image/'

    # 画像を返す
    for r in restaurants_info:
        images_binary = []
        for path in r['ImageFiles']:
            if len(path) != 0:
                with open(IMAGE_DIRECTORY_PATH+path,"r") as f:
                    images_binary.append( f.read() )
        r['ImagesBinary'] = images_binary
    
    # 履歴を保存
    database_functions.save_histories(group_id, user_id, restaurants_info)

    # レスポンスするためにいらないキーを削除する
    response_keys = ['Restaurant_id', 'Name', 'Address', 'CatchCopy', 'Price', 'Category', 'UrlWeb', 'UrlMap', 'ReviewRating', 'BusinessHour', 'Genre', 'Images', 'ImagesBinary']
    response = [{k:v for k,v in r.items() if k in response_keys} for r in restaurants_info] # response_keysに含まれているキーを残す
    return json.dumps(response, ensure_ascii=False)


# ============================================================================================================


@app_.route('/initialize_current_group', methods=['GET','POST'])
def http_initialize_current_group():
    '''
    データベースを初期化
    '''

    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(bind=ENGINE)
    return "complete create_db\n"


@app_.route('/init', methods=['GET','POST'])
def http_init():
    '''
    まだ使われていないグループIDを返す

    Returns
    ----------------
    GroupId
    UserId
    '''

    group_id = database_functions.generate_group_id()
    user_id = generate_user_id()
    result = {'GroupId': str(group_id), 'UserId': str(user_id)}
    return json.dumps(result, ensure_ascii=False)


@app_.route('/invite', methods=['GET', 'POST'])
def http_invite():
    '''
    検索条件を指定して、招待URLを返す

    Returns
    ----------------
    GroupId
    UserId
    Url : 招待URL
    Qr : 招待QRコード
    '''

    URL = 'https://reskima.com'

    # リクエストクエリを受け取る
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
    sort = data["sort"] if data.get("sort", False) else None
    recommend_method = data["recommend_method"] if data.get("recommend_method", False) else RECOMMEND_METHOD
    api_method = data["api_method"] if data.get("api_method", False) else API_METHOD
    
    group_id = group_id if group_id is not None else database_functions.generate_group_id()
    
    # 検索条件をデータベースに保存
    database_functions.set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice, sort)
    
    # 招待URL
    invite_url = URL + '?group_id=' + str(group_id)
    # 招待QRコード
    qr_img = qrcode.make(invite_url)
    buf = BytesIO()
    qr_img.save(buf, format="jpeg")
    qr_img_base64 = base64.b64encode(buf.getvalue()).decode("ascii")
    result = {'GroupId': group_id, 'UserId': generate_user_id(), 'Url': invite_url, 'Qr': qr_img_base64}
    return json.dumps(result, ensure_ascii=False)


@app_.route('/info', methods=['GET','POST'])
def http_info():
    '''
    店情報を要求するリクエスト

    Returns
    ----------------
    restaurants_info : [dict]
    '''

    # リクエストクエリを受け取る
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
    sort = data["sort"] if data.get("sort", False) else None
    recommend_method = data["recommend_method"] if data.get("recommend_method", False) else RECOMMEND_METHOD
    api_method = data["api_method"] if data.get("api_method", False) else API_METHOD

    group_id = group_id if group_id is not None else database_functions.get_group_id(user_id)

    # Yahoo本社の住所 # TODO
    address = "東京都千代田区紀尾井町1-3 東京ガ-デンテラス紀尾井町 紀尾井タワ-"
    lat,lon,address = database_functions.get_lat_lon_address(address)
    # TODO: 開発用に時間を固定
    #open_hour = '18'
    
    # 未登録ならデータベースにユーザとグループを登録する
    fetch_user, fetch_group, fetch_belong = database_functions.register_user_and_group_if_not_exist(group_id, user_id, lat, lon, address, recommend_method, api_method)

    # 検索条件をデータベースに保存
    database_functions.set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice, sort, fetch_group=fetch_group)

    if NEXT_RESPONSE:
        # 他のスレッドで検索中だったら待つ
        if not fetch_belong.writable:
            result = [False]
            while not result[0]:
                time.sleep(1)
                t = threading.Thread(target=thread_info_wait, args=(group_id, user_id, result))
                t.start()
                t.join()
        # 検索して店舗情報を取得
        cache_file = fetch_belong.next_response
        if cache_file is None:
            response = thread_info(False, group_id, user_id, fetch_belong=fetch_belong, fetch_group=fetch_group)
        else:
            # キャッシュを読み込んで、読んだら削除する
            with open(f"data/tmp/{cache_file}") as f:
                response = f.read()
            os.remove(f"data/tmp/{cache_file}")

        # 高速化：次回のアクセスで返す情報を生成しておく
        fetch_belong.next_response = None
        session.commit()
        t = threading.Thread(target=thread_info, args=(True, group_id, user_id))
        t.start()
        return response
    
    else:
        response = thread_info(False, group_id, user_id, fetch_belong=fetch_belong, fetch_group=fetch_group)
        return response

def thread_info_wait(group_id, user_id, result):
    result[0] = session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one().writable

def thread_info(make_cache, group_id, user_id, fetch_belong=None, fetch_group=None):
    import hashlib, base64

    fetch_belong = fetch_belong if fetch_belong is not None else session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()
    fetch_belong.writable = False
    session.commit()

    fetch_group = fetch_group if fetch_group is not None else session.query(Group).filter(Group.id==group_id).one()
    
    if RECOMMEND_PRIORITY:
        restaurants_info = get_restaurants_info_from_recommend_priority(fetch_group, group_id, user_id)
    else:
        restaurants_info = recommend.recommend_main(fetch_group, group_id, user_id)
    
    if restaurants_info is None:
        # error
        restaurants_info = []
        fetch_belong.next_response = None

    # restaurants_infoをテキスト化してdata/tmpにキャッシュとして保存
    response = create_response_from_restaurants_info(restaurants_info)
    if make_cache:
        filename = hashlib.md5(base64.b64encode(str(response).encode())).hexdigest()
        print(f"thread_info: save cache at data/tmp/{filename}")
        with open(f"data/tmp/{filename}", "w")as f:
            f.write(str(response))
        fetch_belong.next_response = filename
    fetch_belong.request_count += 1
    fetch_belong.request_restaurants_num += len(restaurants_info)
    fetch_belong.writable = True
    session.commit()
    return response



@app_.route('/feeling', methods=['GET','POST'])
def http_feeling():
    '''
    キープ・リジェクトの結果を受け取り、メモリに格納する。全会一致の店舗を知らせる。

    Returns
    ----------------
    全会一致の店の数 : int
    '''

    # リクエストクエリを受け取る
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    restaurant_id = data["restaurant_id"] if data.get("restaurant_id", False) else None
    feeling = data["feeling"]

    if user_id is not None and restaurant_id is not None and feeling is not None:

        group_id = group_id if group_id is not None else database_functions.get_group_id(user_id)
        database_functions.update_feeling(group_id, user_id, restaurant_id, feeling) # 投票をデータベースに反映する
        

    # 通知の数を返す。全会一致の店の数
    participants_count = database_functions.get_participants_count(group_id) # 参加人数
    notification_badge = str( session.query(Vote).filter(Vote.group==group_id, Vote.votes_like==participants_count).count() )
    if RECOMMEND_PRIORITY:
        t = threading.Thread(target=thread_feeling, args=(group_id, user_id))
        t.start()
    return notification_badge

def thread_feeling(group_id, user_id):
    fetch_group = session.query(Group).filter(Group.id==group_id).one()
    recommend.recommend_main(fetch_group, group_id, user_id)

@app_.route('/list', methods=['GET','POST'])
def http_list():
    '''
    得票数が多い順の店舗リストを返す。1人のときはキープした店舗のリストを返す。
    リストのアイテムが存在しない場合はnullを返す

    Returns
    ----------------
    restaurants_info : [dict]
    '''

    # リクエストクエリを受け取る
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    group_id = group_id if group_id != None else database_functions.get_group_id(user_id)

    # レストランごとに投票数をカウント
    fetch_votes = session.query(Vote.restaurant, Vote.votes_like).filter(Vote.group==group_id).order_by(desc(Vote.votes_like)).all()
    # リストに存在しない時は空のリストを返す
    if len(fetch_votes) == 0:
        return "[]"
    # 表示する店舗を選ぶ。ひとりのときはLIKEした店だけ。2人以上のときはすべて表示。
    participants_count = database_functions.get_participants_count(group_id) # 参加人数
    restaurant_ids = [h.restaurant for h in fetch_votes if h.votes_all > 0] if participants_count >= 2 else [h.restaurant for h in fetch_votes if h.votes_like > 0]
    fetch_group = session.query(Group).filter(Group.id==group_id).first()
    restaurants_info = api_functions.get_restaurants_info(fetch_group, group_id, restaurant_ids)

    # 得票数が多い順に並べる
    restaurants_info.sort(key=lambda x:x['VotesAll']) # 得票数とオススメ度が同じなら、リジェクトが少ない順
    restaurants_info.sort(key=lambda x:x['RecommendScore'], reverse=True) # 得票数が同じなら、オススメ度順
    restaurants_info.sort(key=lambda x:x['VotesLike'], reverse=True) # 得票数が多い順

    return create_response_from_restaurants_info(restaurants_info)


@app_.route('/history', methods=['GET','POST'])
def http_history():
    '''
    ユーザに表示した店舗履歴のリストを返す。

    Returns
    ----------------
    restaurants_info : [dict]
    '''

    # リクエストクエリを受け取る
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    group_id = group_id if group_id != None else database_functions.get_group_id(user_id)

    # 履歴を取得する
    fetch_histories = session.query(History).filter(History.group==group_id, History.user==user_id).order_by(updated_at).all()
    restaurants_info = api_functions.get_restaurants_info(group_id, [h.restaurant for h in fetch_histories])
    return create_response_from_restaurants_info(restaurants_info)


@app_.route('/decision', methods=['GET','POST'])
def http_decision():
    '''
    現状はアクセスのテスト用,最終決定時のURL
    '''

    # Groupのアーカイブ
    # BelongからGroupをアーカイブ
    # HistoryからGroupをアーカイブ
    # Voteのレストランを削除

    decision_json = {"decision":"test"}
    return decision_json

@app_.route('/test', methods=['GET','POST'])
def http_test():
    '''
    アクセスのテスト用,infoと同じ結果を返す

    Returns
    ----------------
    restaurants_info : [dict]
    '''

    test_restaurants_info = [{"Restaurant_id": "a72a5ed2c330467bd4b4b01a0302bdf977ed00df", 
    "Name": "\u30a8\u30af\u30bb\u30eb\u30b7\u30aa\u30fc\u30eb\u3000\u30ab\u30d5\u30a7\u3000\u30db\u30c6\u30eb\u30b5\u30f3\u30eb\u30fc\u30c8\u8d64\u5742\u5e97", # エクセルシオール　カフェ　ホテルサンルート赤坂店
    "Distance": 492.80934328345614, 
    "CatchCopy": "test", 
    "Price": "test", 
    "TopRankItem": [], 
    "CassetteOwnerLogoImage": "https://iwiz-olp.c.yimg.jp/c/olp/6e/6e6c4795b23a5e45540addb5ff6f0d00/info/55/09/logo/logo_doutor.png", 
    "Images": []
    }]

    return json.dumps(test_restaurants_info)


# アクセスエラー処理
@app_.errorhandler(BadRequest)
@app_.errorhandler(NotFound)
@app_.errorhandler(InternalServerError)
def error_handler(e):
    res = jsonify({ 
                     "error": {
                          "name": e.name,
                          "description": e.description
                      }
                   })
    return res, e.code

