# from sqlalchemy import *
from flask import jsonify, make_response, request, send_file

from app import app_, db_
from app import database_functions, recommend, api_functions, config, call_api
from app.internal_info import *
from app.database_setting import *  # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
import json
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError
import qrcode
from PIL import Image
import base64
from io import BytesIO
import time
import datetime
from sqlalchemy.sql.functions import current_timestamp
import threading
import pprint

# SPEED_UP_FLG
#   Trueにすると高速化できるが、レコメンドの反映が遅れる
#   RecommendSimpleなら NEXT_RESPONSE = True , RECOMMEND_PRIORITY = False 。
#   RecommendSVM   なら NEXT_RESPONSE = False, RECOMMEND_PRIORITY = True  。
NEXT_RESPONSE = config.MyConfig.NEXT_RESPONSE
RECOMMEND_PRIORITY = config.MyConfig.RECOMMEND_PRIORITY

RECOMMEND_METHOD = config.MyConfig.RECOMMEND_METHOD
API_METHOD = config.MyConfig.API_METHOD


def create_response_from_restaurants_info(group_id, user_id, restaurants_info):
    '''
    レスポンスを生成する仕上げ
    '''

    # 画像を返す
    # for r in restaurants_info:
    #     images_binary = []
    #     for path in r['ImageFiles']:
    #         if len(path) != 0:
    #             with open(config.MyConfig.IMAGE_DIRECTORY_PATH+path,"r") as f:
    #                 images_binary.append( f.read() )
    #     r['ImagesBinary'] = images_binary

    # 履歴を保存
    database_functions.save_histories(group_id, user_id, restaurants_info)
    print("create_response_from_restaurants_info:", len(restaurants_info))

    # レスポンスするためにいらないキーを削除する
    restaurants_info = [r.get_dict_for_react() for r in restaurants_info]
    response_keys = ['Restaurant_id', 'Name', 'Address', 'CatchCopy', 'Price',
                     'Category', 'UrlWeb', 'UrlMap', 'ReviewRating',
                     'BusinessHour', 'Genre', 'Images', 'ImagesBinary']
    if config.MyConfig.SHOW_DISTANCE:
        response_keys.append('Distance')
    response = [{k: v for k, v in r.items() if k in response_keys} for r in
                restaurants_info]  # response_keysに含まれているキーを残す
    # pprint.PrettyPrinter(indent=2).pprint(response)

    return json.dumps(response, ensure_ascii=False)


def get_restaurant_ids_from_recommend_priority(fetch_group, group_id,
                                               user_id):
    '''
    Voteテーブルの優先度順にレストランIDを取得する。

    Parameters
    ----------------
    fetch_group
    group_id
    user_id

    Returns
    ----------------
    restaurnt_ids : [dict]
    '''
    session = database_functions.get_db_session()

    histories_restaurants = database_functions.get_histories_restaurants(
        group_id, user_id)
    fetch_votes = session.query(Vote).filter(
        Vote.group == group_id,
        Vote.recommend_priority is not None
    ).order_by(desc(Vote.recommend_priority)).all()

    restaurants_ids = []
    for fv in fetch_votes:
        if fv.restaurant not in histories_restaurants:
            restaurants_ids.append(fv.restaurant)
            if len(restaurants_ids) == config.MyConfig.RESPONSE_COUNT:
                session.close()
                return restaurants_ids

    # まだ優先度を計算していない時や，RecommendSimple等で優先度を計算しない時
    fetch_votes = session.query(Vote).filter(
        Vote.group == group_id,
        Vote.recommend_priority is None
    ).all()
    print(fetch_votes)

    for fv in fetch_votes:
        if fv.restaurant not in histories_restaurants:
            restaurants_ids.append(fv.restaurant)
            if len(restaurants_ids) == config.MyConfig.RESPONSE_COUNT:
                session.close()
                return restaurants_ids
    # ストックしている店舗数が足りない時。最初のリクエスト等。
    session.close()
    return restaurants_ids


# ============================================================================================================


@app_.route('/initialize_current_group', methods=['GET', 'POST'])
def http_initialize_current_group():
    '''
    データベースを初期化
    '''

    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(bind=ENGINE)
    return "complete create_db\n"


@app_.route('/init', methods=['GET', 'POST'])
def http_init():
    '''
    まだ使われていないグループIDを返す

    Returns
    ----------------
    GroupId
    UserId
    '''

    group_id = database_functions.generate_group_id()
    user_id = database_functions.generate_user_id()
    result = {'GroupId': str(group_id), 'UserId': str(user_id)}
    return json.dumps(result, ensure_ascii=False)


@app_.route('/invite', methods=['GET', 'POST'])
def http_invite():
    '''
    グループIDから招待URLを返す

    Returns
    ----------------
    GroupId
    Url : 招待URL
    Qr : 招待QRコード
    '''

    # リクエストクエリを受け取る
    data = request.get_json()["params"]
    group_id = int(data["group_id"]) if data.get("group_id", False) else None

    # 招待URL
    invite_url = 'https://' + config.MyConfig.SERVER_URL + '?group_id=' + str(
        group_id)
    # 招待QRコード
    qr_img = qrcode.make(invite_url)
    buf = BytesIO()
    qr_img.save(buf, format="jpeg")
    qr_img_base64 = base64.b64encode(buf.getvalue()).decode("ascii")
    result = {'GroupId': group_id,
              'Url': invite_url,
              'Qr': qr_img_base64,
              }
    return json.dumps(result, ensure_ascii=False)


@app_.route('/info', methods=['GET', 'POST'])
def http_info():
    '''
    店情報を要求するリクエスト
    threadingでrecommendとget_restaurant_infoをバックグラウンドで行う。
    next_responseからidをRESPONSE_COUNT個とってきて、DBからinfoをとってresponseを作る。

    Returns
    ----------------
    response : [dict]
    '''

    # リクエストクエリを受け取る
    data = request.get_json()["params"]
    pprint.PrettyPrinter(indent=2).pprint(data)

    try:
        user_id = int(data["user_id"])
    except TypeError:
        print("error: http_info")
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    recommend_method = data.get("recommend_method", RECOMMEND_METHOD)
    api_method = data.get("api_method", API_METHOD)

    group_id = group_id if group_id is not None else database_functions.get_group_id(
        user_id)

    # 未登録ならデータベースにユーザとグループを登録する
    (fetch_user,
     fetch_group,
     fetch_belong,
     first_time_group_flg,
     first_time_belong_flg
     ) = database_functions.register_user_and_group_if_not_exist(group_id,
                                                                 user_id,
                                                                 recommend_method,
                                                                 api_method)

    # 検索初期条件をデータベースに保存
    if first_time_group_flg:
        params = Params()
        lat, lon, _ = api_functions.yahoo_contents_geocoder(data.get("place"))
        params.lat = data.get("lat", lat)  # placeがNoneのときはヤフー本社の座標
        params.lon = data.get("lon", lon)
        params.query = data.get("genre")
        try:
            params.open_day = datetime.date.fromisoformat(
                data.get("open_day"))  # 指定不能
        except (TypeError, ValueError):
            params.open_day = datetime.date.today()
        try:
            params.open_hour = datetime.time.fromisoformat(
                data.get("open_hour_str"))
        except (TypeError, ValueError):
            params.open_hour = datetime.datetime.now().time()
        try:
            params.max_price = int(data.get("maxprice"))
        except (TypeError, ValueError):
            params.max_price = None
        try:
            params.min_price = int(data.get("minprice"))  # 指定不能
        except (TypeError, ValueError):
            params.min_price = None
        params.sort = data.get("sort")

        ## パラメーターの初期値を別途計算
        if config.MyConfig.SET_OPEN_HOUR:
            params.open_hour = datetime.time.fromisoformat(
                config.MyConfig.OPEN_HOUR)

        database_functions.set_search_params(group_id,
                                             params,
                                             fetch_group=fetch_group)

        # 初回優先度を計算
        _ = recommend.recommend_main(fetch_group, group_id, user_id,
                                     first_time_flg=first_time_group_flg)

    ## priorityの高い順にid取得
    restaurant_ids = get_restaurant_ids_from_recommend_priority(fetch_group,
                                                                group_id,
                                                                user_id)

    ## responseを作る
    restaurants_info = database_functions.load_restaurants_info(
        restaurant_ids, group_id)
    response = create_response_from_restaurants_info(group_id, user_id,
                                                     restaurants_info)

    if first_time_group_flg:
        # 裏でrecommendを走らせる
        ## 他のスレッドで更新中だったら何もしない
        session = database_functions.get_db_session()
        fetch_group = session.query(Group).filter(Group.id==group_id).one()
        if fetch_group.writable:
            t = threading.Thread(target=thread_info,
                                 args=(group_id,
                                       user_id,
                                       fetch_belong,
                                       fetch_group
                                       ))
            t.start()

        session.close()
    return response


def thread_info(group_id, user_id, fetch_belong, fetch_group):
    """
    裏でrecommend_mainを実行する。
    recommend_mainの中でget_restaurant_infoまで処理する。

    Parameters
    ----------
    group_id
    user_id
    fetch_belong
    fetch_group

    Returns
    -------

    """
    session = database_functions.get_db_session()
    fetch_group = session.query(Group).filter(Group.id == group_id).one()
    
    # 他に待機中のスレッドがあれば、このスレッドは破棄
    if fetch_group.wait_calc_priority:
        session.close()
        print("calc_priority_thread: dispose")
        return

    ## 他のスレッドで更新中だったら待つ
    if not fetch_group.writable:
    
        fetch_group.wait_calc_priority = True
        session.commit()

        result = False
        while not result:
            print("calc_priority_thread: waiting")
            time.sleep(1)
            session.commit()
            result = session.query(Group).filter(Group.id == group_id).one().writable
        
        fetch_group.wait_calc_priority = False
        session.commit()
    
    # 店舗情報取得と優先度計算
    fetch_group.writable = False
    session.commit()

    _ = recommend.recommend_main(fetch_group, group_id, user_id)

    fetch_group.writable = True
    session.commit()
    session.close()
    print("calc_priority_thread: end")
    return


@app_.route('/feeling', methods=['GET', 'POST'])
def http_feeling():
    '''
    キープ・リジェクトの結果を受け取り、メモリに格納する。全会一致の店舗を知らせる。

    Returns
    ----------------
    全会一致の店の数 : int
    '''
    session = database_functions.get_db_session()

    # リクエストクエリを受け取る
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    restaurant_id = data["restaurant_id"] if data.get("restaurant_id",
                                                      False) else None
    feeling = data["feeling"]

    group_id = group_id if group_id is not None else database_functions.get_group_id(
        user_id)

    if user_id is not None and restaurant_id is not None and feeling is not None:
        database_functions.update_feeling(group_id, user_id, restaurant_id,
                                          feeling)  # 投票をデータベースに反映する

    # 通知の数を返す。全会一致の店の数
    participants_count = database_functions.get_participants_count(
        group_id)  # 参加人数
    notification_badge = str(session.query(Vote).filter(Vote.group == group_id,
                                                        Vote.votes_like == participants_count).count())
    if RECOMMEND_PRIORITY:
        # 裏でrecommendを走らせる

        fetch_group = session.query(Group).filter(Group.id == group_id).first()
        fetch_belong = session.query(Belong).filter(Belong.user == user_id,
                                                    Belong.group == group_id
                                                    ).first()
        t = threading.Thread(target=thread_info,
                             args=(group_id,
                                   user_id,
                                   fetch_belong,
                                   fetch_group
                                   ))
        t.start()
    session.close()
    return notification_badge


@app_.route('/list', methods=['GET', 'POST'])
def http_list():
    '''
    得票数が多い順の店舗リストを返す。1人のときはキープした店舗のリストを返す。
    リストのアイテムが存在しない場合はnullを返す

    Returns
    ----------------
    restaurants_info : [dict]
    '''
    session = database_functions.get_db_session()

    # リクエストクエリを受け取る
    data = request.get_json()["params"]
    user_id = int(data["user_id"]) if data.get("user_id", False) else None
    group_id = int(data["group_id"]) if data.get("group_id", False) else None
    group_id = group_id if group_id != None else database_functions.get_group_id(
        user_id)

    # レストランごとに投票数をカウント
    fetch_votes = session.query(Vote).filter(
        Vote.group == group_id).order_by(desc(Vote.votes_like)).all()
    # リストに存在しない時は空のリストを返す
    if len(fetch_votes) == 0:
        session.close()
        return "[]"
    # 表示する店舗を選ぶ。ひとりのときはLIKEした店だけ。2人以上のときはすべて表示。
    participants_count = database_functions.get_participants_count(
        group_id)  # 参加人数
    restaurant_ids = [h.restaurant for h in fetch_votes if
                      h.votes_all > 0] if participants_count >= 2 else [
        h.restaurant for h in fetch_votes if h.votes_like > 0]
    fetch_group = session.query(Group).filter(Group.id == group_id).first()
    restaurants_info = database_functions.load_restaurants_info(restaurant_ids,
                                                                group_id
                                                                )

    # 得票数が多い順に並べる
    restaurants_info.sort(
        key=lambda x: x.votes_all)  # 得票数とオススメ度が同じなら、リジェクトが少ない順
    restaurants_info.sort(key=lambda x: x.recommend_score,
                          reverse=True)  # 得票数が同じなら、オススメ度順
    restaurants_info.sort(key=lambda x: x.votes_like, reverse=True)  # 得票数が多い順

    session.close()
    return create_response_from_restaurants_info(group_id, user_id,
                                                 restaurants_info)


@app_.route('/history', methods=['GET', 'POST'])
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
    group_id = group_id if group_id != None else database_functions.get_group_id(
        user_id)

    # 履歴を取得する
    session = database_functions.get_db_session()
    restaurant_ids = session.query(History.id).filter(History.group == group_id,
                                                      History.user == user_id
                                                      ).order_by(
        updated_at).all()
    session.close()
    restaurants_info = database_functions.load_restaurants_info(restaurant_ids,
                                                                group_id
                                                                )
    return create_response_from_restaurants_info(group_id, user_id,
                                                 restaurants_info)


@app_.route('/decision', methods=['GET', 'POST'])
def http_decision():
    '''
    現状はアクセスのテスト用,最終決定時のURL
    '''

    # Groupのアーカイブ
    # BelongからGroupをアーカイブ
    # HistoryからGroupをアーカイブ
    # Voteのレストランを削除

    decision_json = {"decision": "test"}
    return decision_json


@app_.route('/image', methods=['GET'])
def http_image():
    name = request.args.get('name')
    print(f"http_image: name={name}")
    return send_file(f"../{config.MyConfig.IMAGE_DIRECTORY_PATH}{name}")


@app_.route('/test', methods=['GET', 'POST'])
def http_test():
    '''
    アクセスのテスト用,infoと同じ結果を返す

    Returns
    ----------------
    restaurants_info : [dict]
    '''

    test_restaurants_info = [
        {"Restaurant_id": "a72a5ed2c330467bd4b4b01a0302bdf977ed00df",
         "Name": "\u30a8\u30af\u30bb\u30eb\u30b7\u30aa\u30fc\u30eb\u3000\u30ab\u30d5\u30a7\u3000\u30db\u30c6\u30eb\u30b5\u30f3\u30eb\u30fc\u30c8\u8d64\u5742\u5e97",
         # エクセルシオール　カフェ　ホテルサンルート赤坂店
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
