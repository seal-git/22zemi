# from sqlalchemy import *
from flask import jsonify, make_response, request
from app import app_, db_
from app import recommend, api_functions
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from random import randint
import json
from werkzeug.exceptions import NotFound,BadRequest,InternalServerError
import datetime
import qrcode
from PIL import Image
import base64
from io import BytesIO
import time
import requests
import sqlalchemy
from sqlalchemy.sql.functions import current_timestamp
import threading


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


def set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice, sort, fetch_group=None):
    '''
    検索条件を受け取り、データベースのグループの表を更新する。
    '''
    if place is None and genre is None and query is None and open_hour is None and maxprice is None and minprice is None and sort is None: return
    
    if fetch_group is None:
        fetch_group = session.query(Group).filter(Group.id==group_id).first()

    if place is not None:
        lat,lon,address = get_lat_lon_address(place)
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
    fetch_group.sort = sort

    session.commit()


def get_lat_lon_address(query):
    '''
    Yahoo APIを使って、緯度・経度・住所を返す関数

    Parameters
    ----------------
    query : string
        場所のキーワードや住所
        例：千代田区
    
    Returns
    ----------------
    lat, lon : float
        queryで入力したキーワード周辺の緯度経度を返す
        例：lat = 35.69404120, lon = 139.75358630
    address : string
        住所

    例外処理
    ----------------
    不適切なqueryを入力した場合、Yahoo!本社の座標を返す
    '''

    geo_coder_url = "https://map.yahooapis.jp/geocode/cont/V1/contentsGeoCoder"
    params = {
        "appid": os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        "output": "json",
        "query": query
    }
    try:
        response = requests.get(geo_coder_url, params=params)
        response = response.json()
        geometry = response["Feature"][0]["Geometry"]
        coordinates = geometry["Coordinates"].split(",")
        lon = float(coordinates[0])
        lat = float(coordinates[1])
        address = response["Feature"][0]["Property"]["Address"]
    except:
        # Yahoo!本社の座標
        lon = 139.73284
        lat = 35.68001 
        address = "東京都千代田区紀尾井町1-3 東京ガ-デンテラス紀尾井町 紀尾井タワ-"
        
    return lat, lon, address


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

    group_id = generate_group_id()
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
    recommend_method = data["recommend_method"] if data.get("recommend_method", False) else None
    api_method = data["api_method"] if data.get("api_method", False) else None
    
    group_id = group_id if group_id is not None else generate_group_id()
    
    # 検索条件をデータベースに保存
    set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice, sort)
    
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
    recommend_method = data["recommend_method"] if data.get("recommend_method", False) else None
    api_method = data["api_method"] if data.get("api_method", False) else None
    api_method = "yahoo"


    group_id = group_id if group_id is not None else get_group_id(user_id)

    # Yahoo本社の住所 # TODO
    address = "東京都千代田区紀尾井町1-3 東京ガ-デンテラス紀尾井町 紀尾井タワ-"
    lat,lon,address = get_lat_lon_address(address)
    # TODO: 開発用に時間を固定
    #open_hour = '18'
    
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
        new_group.api_method = api_method
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

    # 検索条件をデータベースに保存
    set_filter_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice, sort, fetch_group=fetch_group)

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
        response = thread_info(group_id, user_id, fetch_belong=fetch_belong, fetch_group=fetch_group)
    else:
        # キャッシュを読み込んで、読んだら削除する
        with open(f"data/tmp/{cache_file}") as f:
            response = f.read()
        os.remove(f"data/tmp/{cache_file}")

    # 高速化：次回のアクセスで返す情報を生成しておく
    fetch_belong.next_response = None
    session.commit()
    t = threading.Thread(target=thread_info, args=(group_id, user_id))
    t.start()
    return response

def thread_info_wait(group_id, user_id, result):
    result[0] = session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one().writable

def thread_info(group_id, user_id, fetch_belong=None, fetch_group=None):
    import hashlib
    import base64
    fetch_belong = fetch_belong if fetch_belong is not None else session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()
    fetch_belong.writable = False

    session.commit()
    fetch_group = fetch_group if fetch_group is not None else session.query(Group).filter(Group.id==group_id).one()
    restaurants_info = recommend.recommend_main(fetch_group, group_id, user_id)
    
    if restaurants_info is None:
        # error
        restaurants_info = []
        fetch_belong.next_response = None

    # restaurants_infoをテキスト化してdata/tmpにキャッシュとして保存
    response = create_response_from_restaurants_info(restaurants_info)
    filename = hashlib.md5(base64.b64encode(str(response).encode())).hexdigest()
    print(filename)
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

        group_id = group_id if group_id is not None else get_group_id(user_id)
        
        # 履歴にfeelingを登録
        fetch_history = session.query(History).filter(History.group==group_id, History.user==user_id, History.restaurant==restaurant_id).first()
        if fetch_history is not None:
            prev_feeling = fetch_history.feeling
            fetch_history.feeling = feeling
            session.commit()
        else:
            # ここは実行されないはず
            print("models.py/feeling: error")
            prev_feeling = None
            new_history = History()
            new_history.group = group_id
            new_history.user = user_id
            new_history.restaurant = restaurant_id
            new_history.feeling = feeling
            session.add(new_history)
            session.commit()
        
        # 投票数を更新
        fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==restaurant_id).first()
        if fetch_vote is not None:
            fetch_vote.votes_all += 1 if prev_feeling is None else 0
            fetch_vote.votes_like += (1 if feeling else 0) if prev_feeling is None else ((0 if feeling else -1) if prev_feeling else (1 if feeling else 0))
            session.commit()
        else:
            # ここは実行されないはず
            new_vote = Vote()
            new_vote.group = group_id
            new_vote.restaurant = restaurant_id
            new_vote.votes_all = 1
            new_vote.votes_like = 1 if feeling else 0
            session.add(new_vote)
            session.commit()

    # 通知の数を返す。全会一致の店の数
    alln = session.query(Belong).filter(Belong.group==group_id).count() # 参加人数
    return str( session.query(Vote).filter(Vote.group==group_id, Vote.votes_like==alln).count() )


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
    group_id = group_id if group_id != None else get_group_id(user_id)

    # レストランごとに投票数をカウント
    fetch_votes = session.query(Vote.restaurant, Vote.votes_like).filter(Vote.group==group_id).order_by(desc(Vote.votes_like)).all()
    # リストに存在しない時は空のリストを返す
    if len(fetch_votes) == 0:
        return "[]"
    # 表示する店舗を選ぶ。ひとりのときはLIKEした店だけ。2人以上のときはすべて表示。
    alln = session.query(Belong).filter(Belong.group==group_id).count() # 参加人数
    restaurant_ids = [h.restaurant for h in fetch_votes if h.votes_all > 0] if alln >= 2 else [h.restaurant for h in fetch_votes if h.votes_like > 0]
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
    group_id = group_id if group_id != None else get_group_id(user_id)

    # 履歴を取得する
    fetch_histories = session.query(History.restaurant).filter(History.group==group_id, History.user==user_id).order_by(updated_at).all()
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
                          "name": error.name, 
                          "description": error.description 
                      }
                   })
    return res, e.code

