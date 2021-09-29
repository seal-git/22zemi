import requests
import os
import datetime
from app import database_functions, calc_info, config
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from app.database_setting import *  # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from app.internal_info import *
from abc import ABCMeta, abstractmethod
from flask import abort
import pprint
import re
import urllib

# from PIL import Image
# from io import BytesIO


'''
APIを叩いてinternal_infoに変換する。
新しいAPIを追加する場合は、RestaurantInfoを入力してRestrantInfoを返すようにする。
つまり、RestaurantInfoの内部情報をAPIで更新していくイメージ。
'''

def yahoo_review(r_info):
    '''
    Yahoo APIにアクセスして口コミを取得する。reviewとratingに保存する。
    '''
    # print("get_rating")
    review_api_url = 'https://map.yahooapis.jp/olp/v1/review/' + r_info.yahoo_id
    params = {
        "appid": os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        "output": "json",
        "results": "100"
    }
    try:
        response = requests.get(review_api_url, params=params)
        response = response.json()
    except:
        response["Feature"] = []

    review_list = response["Feature"]
    if len(review_list) == 0: return r_info
    pprint.PrettyPrinter(indent=2).pprint(review_list)
    r_info.review += [review_list['Property']['Comment']['Rating'] for r in
                     review_list]

    return r_info


def yahoo_contents_geocoder(query):
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

    # Yahoo!本社の座標
    lon = 139.73284
    lat = 35.68001
    address = "東京都千代田区紀尾井町1-3 東京ガ-デンテラス紀尾井町 紀尾井タワ-"
    if query is None:
        return lat, lon, address

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
        pass

    return lat, lon, address


def yahoo_local_search(params: Params = None,
                       r_info: RestaurantInfo = None,
                       r_id: str = None):
    """
    yahoo localsearchを使ってRestaruantInfoのリストを返す。
    Parameters
    ----------
    params
    r_info
    どちらかが入力されていればそれに応じて検索する
    Returns
    -------
    """
    if params is not None:
        # paramsで検索
        print(f"yahoo_local_search with params")
        pprint.PrettyPrinter(indent=2).pprint(params.get_all())
        ## distの計算
        if params.max_dist is not None:
            dist = params.max_dist / 1000
        else:
            dist = config.MyConfig.MAX_DISTANCE / 1000
        ## sortのチェック
        sort_param = ["rating", "score", "hybrid", "review", "kana", "price",
                      "dist", "geo", "match"]
        sort_param += ["-" + i for i in sort_param]
        sort = params.sort if params.sort in sort_param else "hybrid"
        ## boolの変換
        image = "true" if params.image else None
        loco_mode = "true" if params.loco_mode else None
        ## 時間指定
        if params.open_hour is not None:
            # open = str(params.open_day) + "," + str(params.open_hour)
            open = None  # 時間の設定されている店は少ないので指定しない
        else:
            open = "now"

        ## パラメータをdictにして返す
        params_dict = {
            "query": params.query,
            "results": params.results,
            "start": params.start,
            "lat": params.lat,
            "lon": params.lon,
            "sort": sort,
            "dist": dist,
            "image": image,
            "maxprice": params.max_price,
            "minprice": params.min_price,
            "loco_mode": loco_mode,
            "open": open,
        }
    elif r_info is not None:
        # restaurant_infoで検索
        # print(f"yahoo_local_search with r_info")
        if r_info.yahoo_id is not None:
            params_dict = {
                "uid": r_info.yahoo_id
            }
        else:
            params_dict = {
                "query": r_info.name
            }
    else:
        raise ValueError(f"Both params and restaurant_info don't exist.")

    # APIで検索を実行
    local_search_url = 'https://map.yahooapis.jp/search/local/V1/localSearch'
    params_dict.update({
        'appid': os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        'output': 'json',
        'gc': '01',
        'detail': 'full',
    })
    pprint.PrettyPrinter(indent=2).pprint(params_dict)
    try:
        response = requests.get(local_search_url, params=params_dict).json()
    except Exception as e:
        abort(e.code)

    # 検索の該当が無かったとき
    if response['ResultInfo']['Count'] == 0:
        print("yahoo local search: result 0")
        return []

    # responseをrestaurant_infoに変換
    restaurants_info = []
    feature_list = response['Feature']
    pprint.PrettyPrinter(indent=2).pprint(feature_list)
    [pprint.PrettyPrinter(indent=2).pprint(f["Property"]["Detail"]["CassetteOwner"]) for f  in feature_list]

    for feature in feature_list:
        if params is not None:
            r_info = RestaurantInfo()
            r_info.id = feature['Property']['Uid']

        r_info.yahoo_id = feature['Property']['Uid']
        r_info.name = feature['Name']
        r_info.address = feature['Property'].get('Address')
        r_info.lon, r_info.lat = tuple(
            [float(x) for x in feature['Geometry']['Coordinates'].split(',')])
        r_info.station = [s["Name"] for s in feature["Property"]["Station"]]
        r_info.railway = [s["Railway"] for s in feature["Property"]["Station"]]
        r_info.catchcopy = feature['Property'].get('CatchCopy')
        r_info.lunch_price = feature['Property']['Detail'].get('LunchPrice')
        if r_info.lunch_price is not None: r_info.lunch_price = int(r_info.lunch_price)
        r_info.dinner_price = feature['Property']['Detail'].get('DinnerPrice')
        if r_info.dinner_price is not None: r_info.dinner_price = int(r_info.dinner_price)
        r_info.category = feature['Property'].get('Genre',[{'Name':None}])[0]['Name']
        r_info.genre = [feature['Property'].get('Genre',[{'Name':None}])[0]['Name']]
        r_info.web_url = "https://loco.yahoo.co.jp/place/" + feature['Property']['Uid']
        r_info.monday_opening_hours = feature["Property"].get("MondayBusinessHour")
        r_info.tuesday_opening_hours = feature["Property"].get("TuesdayBusinessHour")
        r_info.wednesday_opening_hours = feature["Property"].get("WednesdayBusinessHour")
        r_info.thursday_opening_hours = feature["Property"].get("ThursdayBusinessHour")
        r_info.friday_opening_hours = feature["Property"].get("FridayBusinessHour")
        r_info.saturday_opening_hours = feature["Property"].get("SaturdayBusinessHour")
        r_info.sunday_opening_hours = feature["Property"].get("SundayBusinessHour")
        r_info.access = feature["Property"].get("Access1")
        r_info.health_info = feature["Property"].get("HealthInfo")
        r_info.yahoo_rating_float = feature["Property"].get("Rating")

        # レガシーなパラメータ
        # restaurant_info['TopRankItem'] = [
        #     feature['Property']['Detail']['TopRankItem' + str(j)] for j in
        #     range(MAX_LIST_COUNT) if 'TopRankItem' + str(j) in feature['Property'][
        #         'Detail']]  # TopRankItem1, TopRankItem2 ... のキーをリストに。
        # restaurant_info['CassetteOwnerLogoImage'] = feature['Property']['Detail'].get(
        #     'CassetteOwnerLogoImage')
        # r_info.map_url = "https://map.yahoo.co.jp/route/walk?from=" + str(
        #     fetch_group.address) + "&to=" + feature['Property']['Address']
        # r_info['BusinessHour'] = (
        #     feature['Property']['Detail'].get('BusinessHour')).replace('<br>', '\n').replace(
        #     '<br />', '') if feature['Property']['Detail'].get(
        #     'BusinessHour') is not None else ""

        # Images : 画像をリストにする
        images = []
        for key, value in feature['Property']['Detail'].items():
            if re.fullmatch(r"Image\d+|PersistencyImage\d|ItemImageUrl\d|CassetteOwnerLogoImage", key):
                images.append(value)
        # 画像が1枚もないときはnoimageを出力
        if len(images) == 0:
            no_image_url = "http://drive.google.com/uc?export=view&id=1mUBPWv3kL-1u2K8LFe8p_tL3DoU65FJn"
            images = [no_image_url]

        r_info.image_url = list(set(images)) # setで重複をなくす
        if len(r_info.image_url)>config.MyConfig.MAX_LIST_COUNT:
            r_info.image_url = r_info.image_url[:config.MyConfig.MAX_LIST_COUNT]

        restaurants_info.append(r_info)

    return restaurants_info


def google_nearby_search(params):
    '''
    Google APIで店舗情報(feature)を取得する。

    Parameters
    ----------------
    fetch_group :
        データベースのグループ情報
    group_id : int
        groupID
    search_params : dict
        Yahoo local search APIに送信するクエリ

    Returns
    ----------------
    restaurants_info : [dict]
        レスポンスするレストラン情報をjson形式で返す。
    '''

    print(f"google nearby search:")
    if params.lat is not None and params.lon is not None:
        location = str(params.lat) + "," + str(params.lon)  # 緯度経度
    if params.max_price is not None: maxprice = min(params.max_price / 2500, 4.0)
    if params.min_price is not None: minprice = min(params.min_price / 2500, 4.0)
    rankby = "distance" if params.sort in ["dist", "geo"] else "prominence"

    search_params = {
        "keyword": params.query,
        "location": location,
        "radius": params.max_dist,
        "maxprice": maxprice,
        "minprice": minprice,
        "rankby": rankby,
    }

    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'  # 緯度経度と半径からお店を取得
    search_params.update({
        'key': os.environ['GOOGLE_API_KEY'],
        'output': 'json',
        'type': 'restaurant'
    })  # 検索クエリの設定(詳しくはPlace Search APIのドキュメント参照)

    response = requests.get(url=url, params=search_params)
    local_search_json = response.json()  # レスポンスのjsonをdict型にする

    # 検索の該当が無かったとき
    if len(local_search_json['results']) == 0:
        print("nearby search:result 0")
        return []

    # apiで受け取ったjsonをクライアントアプリに送るjsonに変換する
    restaurants_info = []
    for i, res in enumerate(local_search_json['results']):  # 最大20件まで取れる
        r_info = RestaurantInfo()
        r_info.id = res["place_id"]
        r_info.google_id = res["place_id"]
        restaurants_info.append(r_info)

    return restaurants_info


def google_text_search(params):
    print(f"google text search:")
    if params.lat is not None and params.lon is not None:
        location = str(params.lat) + "," + str(params.lon)  # 緯度経度
    if params.max_price is not None: maxprice = min(params.max_price / 2500, 4.0)
    if params.min_price is not None: minprice = min(params.min_price / 2500, 4.0)
    search_params = {
        "query": params.query,
        "location": location,
        "radius": params.max_dist,
        "maxprice": maxprice,
        "minprice": minprice,
    }

    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'  # 緯度経度と半径からお店を取得
    params.update({
        'key': os.environ['GOOGLE_API_KEY'],
        'output': 'json',
        'type': 'restaurant',
        'language': 'ja'
    })  # 検索クエリの設定(詳しくはPlace Search APIのドキュメント参照)

    response = requests.get(url=url, params=search_params)
    local_search_json = response.json()  # レスポンスのjsonをdict型にする

    # 検索の該当が無かったとき
    if len(local_search_json['results']) == 0:
        print("text search: result 0")
        return []

    # apiで受け取ったjsonをクライアントアプリに送るjsonに変換する
    restaurants_info = []
    for i, res in enumerate(local_search_json['results']):  # 最大20件まで取れる
        r_info = RestaurantInfo()
        r_info.id = res["place_id"]
        r_info.google_id = res["place_id"]
        restaurants_info.append(r_info)

    return restaurants_info



def google_find_place(r_info):
    """
    google find placeでお店のgoogle_idを取得
    Parameters
    ----------
    r_info

    Returns
    -------
    r_info
    """
    # place検索
    print(f"find place: {r_info.name}")
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    params = {
        'key': os.environ["GOOGLE_API_KEY"],
        'input': r_info.name,
        'inputtype': 'textquery',
        'fields': 'place_id'
    }
    res = requests.get(url=url, params=params)
    # pprint.PrettyPrinter(indent=2).pprint(res.json())
    res = res.json()['candidates'][0]

    if r_info.id is None: r_info.id = res['place_id']
    r_info.google_id = res['place_id']

    return r_info

def google_place_details(r_info:RestaurantInfo=None):
    """
    place_detailを取得

    Parameters
    ----------
    r_info

    Returns
    -------

    """
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'key': os.environ["GOOGLE_API_KEY"],
        'place_id': r_info.google_id,
        'language': 'ja',
        'fields': 'name,photo,rating,review'
    }
    res = requests.get(url=url, params=params)
    res = res.json()['result']
    # pprint.PrettyPrinter(indent=2).pprint(res)

    if r_info.name is None: r_info.name = res.get("name")
    if r_info.address is None: r_info.address = res.get("formatted_address")
    # if r_info.lat is None: r_info.lat = res.get("geometry")["location"]["lat"]
    # if r_info.lon is None: r_info.lon = res.get("geometry")["location"]["lng"]

    r_info.google_rating = res.get("rating")
    if res.get("reviews") is not None:
        r_info.review += [r["text"] for r in res.get("reviews")]
    r_info.google_photo_reference = [r["photo_reference"] for r in res.get("photos")]
    # TODO: xxxday_opening_hoursを取得する
    return r_info


def google_feature_to_info(self, fetch_group, group_id, feature):
    '''
    Google APIで取得した店舗情報(feature)を、クライアントに送信するjsonの形式に変換する。
    じきに消す

    Parameters
    ----------------
    fetch_group :
        データベースのグループ情報
    group_id: int
        グループID
    lunch_or_dinner:
        現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
    feature : dict
        Google APIで取得した店舗情報

    Returns
    ----------------
    restaurant_info : dict
        レスポンスするレストラン情報をjson形式で返す。
    '''

    MAX_LIST_COUNT = 10

    restaurant_info = {}
    restaurant_id = feature['place_id']
    restaurant_info['Restaurant_id'] = restaurant_id
    restaurant_info['Name'] = feature['name']
    restaurant_info['Address'] = feature[
        'formatted_address'] if 'formatted_address' in feature.keys() else ""
    restaurant_info['CatchCopy'] = ""
    restaurant_info['Price'] = feature['plus_code']['price_level'] if 'price_level' in \
                                                                      feature[
                                                                          'plus_code'].keys() else 0
    restaurant_info['LunchPrice'] = feature['plus_code'][
        'price_level'] if 'price_level' in feature['plus_code'].keys() else 0
    restaurant_info['DinnerPrice'] = feature['plus_code'][
        'price_level'] if 'price_level' in feature['plus_code'].keys() else 0
    restaurant_info[
        'TopRankItem'] = []  # [feature['Property']['Detail']['TopRankItem'+str(j)] for j in range(MAX_LIST_COUNT) if 'TopRankItem'+str(j) in feature['Property']['Detail']] # TopRankItem1, TopRankItem2 ... のキーをリストに。
    restaurant_info['CassetteOwnerLogoImage'] = feature['icon']
    restaurant_info['Category'] = feature['types'][0]
    restaurant_info['UrlWeb'] = feature['website'] if 'website' in feature.keys() else ""
    restaurant_info['UrlMap'] = feature['url'] if 'url' in feature.keys() else ""
    restaurant_info['ReviewRating'] = self.get_review_rating_string(
        feature['rating']) if 'rating' in feature.keys() else ""
    restaurant_info['ReviewRatingFloat'] = float(feature['rating'])
    restaurant_info['BusinessHour'] = feature['opening_hours']['weekday_text'] if (
                                                                                              'opening_hours' in feature.keys()) and (
                                                                                              'weekday_text' in
                                                                                              feature[
                                                                                                  'opening_hours'].keys()) else "unknown"
    restaurant_info['Genre'] = [{'Code': '0', 'Name': 'UnKnown'}]
    # [{'Code': '0110005', 'Name': 'ビアホール'}]この形式にしたい
    restaurant_info['Lat'], restaurant_info['Lon'] = feature['geometry'][
        'location'].values()

    # Images : 画像をリストにする
    photo_references = [photo['photo_reference'] for photo in
                        feature['photos']]  # photo_referenceを複数取得
    photo_nums = 3  # 画像のURL数
    # restaurant_info['ImageFiles'] = calc_info.create_image(restaurant_info)
    restaurant_info['Images'] = self.get_place_photo_urls(photo_references, photo_nums)
    if len(restaurant_info["Images"]) == 0:
        no_image_url = "http://drive.google.com/uc?export=view&id=1mUBPWv3kL-1u2K8LFe8p_tL3DoU65FJn"
        restaurant_info["Images"] = [no_image_url, no_image_url]

    return restaurant_info


