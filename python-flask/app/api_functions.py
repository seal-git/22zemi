import requests
import os
import datetime
from app.database_setting import *  # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from app.internal_info import *
from abc import ABCMeta, abstractmethod
from flask import abort
import pprint
import re

# from PIL import Image
# from io import BytesIO


'''

APIで店舗情報を取得する。
========
search_restaurants_infoとget_restaurants_infoが最初に呼ばれる。

# 新しいAPIの記述
 - ApiFunctionsクラスを継承して記述してください。
 - ApiFunctionsYahooクラスを参考にしてください
 - search_restaurants_info関数とget_restaurants_info関数に作ったクラスを追加してください。

# 主な流れ
search_restaurants_info関数は検索条件(search_params)から店の情報(restaurants_info)を取得する。
get_restaurants_info関数は検索条件(restaurant_ids)から店の情報(restaurants_info)を取得する。

# 主な変数
restaurants_info: [dict]
    ユーザにレスポンスするjson
search_params : dict
    Yahoo Local Search API の検索クエリと一緒
restaurant_ids : [string]
    レストランIDのリスト

calc_info.pyにapi_functions.py関係の関数があります。
'''


# ============================================================================================================
# ApiFunctionsクラス関連


def get_rating(r_info):
    '''
    Yahoo APIにアクセスして口コミを見ます
    '''
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

    r_info.review = [review_list['Property']['Comment']['Rating'] for r in
                     review_list]

    return r_info


def yahoo_local_search(params: Params = None, r_info: RestaurantInfo = None):
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
    print(f"yahoo_local_search")

    # paramsをyahoo用の検索クエリに変換
    if params is not None:
        ## distの計算
        if params.max_dist is not None:
            dist = params.max_dist / 1000
        else:
            dist = config.MyConfig.MAX_DISTANCE
        ## sortのチェック
        sort_param = ["rating", "score", "hybrid", "review", "kana", "price",
                      "dist", "geo", "match"]
        sort_param += ["-" + i for i in sort_param]
        sort = params.sort if params.sort in sort_param else "hybrid"
        ## boolの変換
        image = "true" if params.image else None
        loco_mode = "true" if params.loco_mode else None
        ## 時間指定
        if params.open_day is not None and params.open_hour is not None:
            open = str(params.open_day) + "," + str(params.open_hour)
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
        'detail': 'full'
    })
    try:
        response = requests.get(local_search_url, params=params_dict).json()
    except Exception as e:
        abort(e.code)

    # 検索の該当が無かったとき
    if response['ResultInfo']['Count'] == 0:
        return []

    # responseをrestaurant_infoに変換
    feature_list = response['Feature']
    # pprint.PrettyPrinter(indent=2).pprint(feature_list)

    restaurants_info = []

    for feature in feature_list:
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
        r_info.dinner_price = feature['Property']['Detail'].get('DinnerPrice')
        r_info.category = feature['Property'].get('Genre')[0]['Name']
        r_info.genre = [feature['Property'].get('Genre')[0]['Name']]
        r_info.web_url = "https://loco.yahoo.co.jp/place/" + feature['Property']['Uid']
        r_info.monday_opening_hours = feature["Property"]["MondayBusinessHour"]
        r_info.tuesday_opening_hours = feature["Property"]["TuesdayBusinessHour"]
        r_info.wednesday_opening_hours = feature["Property"]["WednesdayBusinessHour"]
        r_info.thursday_opening_hours = feature["Property"]["ThursdayBusinessHour"]
        r_info.friday_opening_hours = feature["Property"]["FridayBusinessHour"]
        r_info.saturday_opening_hours = feature["Property"]["SaturdayBusinessHour"]
        r_info.sunday_opening_hours = feature["Property"]["SundayBusinessHour"]
        r_info.access = feature["Property"].get("Access1")
        r_info.health_info = feature["Property"].get("HealthInfo")

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
            if re.fullmatch(r"Image\d+|PersistencyImage\d|ItemImageUrl\d", key):
                images.append(value)

        r_info.image_url = images

        restaurants_info.append(r_info)

    return restaurants_info


def feature_to_info(self, fetch_group, group_id, lunch_or_dinner, feature, access_flag):
    '''
    Yahoo local search APIで取得した店舗情報(feature)を、クライアントに送信するjsonの形式に変換する。

    Parameters
    ----------------
    fetch_group :
        データベースのグループ情報
    group_id: int
        グループID
    lunch_or_dinner:
        現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
    feature : dict
        Yahoo local search APIで取得した店舗情報

    Returns
    ----------------
    restaurant_info : dict
        レスポンスするレストラン情報をjson形式で返す。
    '''
    # print(f"feature_to_info(api_yahoo):{access_flag}")

    MAX_LIST_COUNT = 10

    if access_flag == 'get': print(f"feature_to_info(api_yahoo):{access_flag}")

    restaurant_info = {}
    restaurant_id = feature['Property']['Uid']
    restaurant_info['Restaurant_id'] = restaurant_id
    restaurant_info['Name'] = feature['Name']
    restaurant_info['Address'] = feature['Property']['Address']
    restaurant_info['CatchCopy'] = feature['Property'].get('CatchCopy')
    restaurant_info['Price'] = feature['Property']['Detail'][
        'LunchPrice'] if lunch_or_dinner == 'lunch' and feature['Property']['Detail'].get(
        'LunchFlag') == True else feature['Property']['Detail'].get('DinnerPrice')
    restaurant_info['Price'] = int(restaurant_info['Price']) if type(
        restaurant_info['Price']) is str else restaurant_info['Price']
    restaurant_info['LunchPrice'] = feature['Property']['Detail'].get('LunchPrice')
    restaurant_info['DinnerPrice'] = feature['Property']['Detail'].get('DinnerPrice')
    restaurant_info['TopRankItem'] = [
        feature['Property']['Detail']['TopRankItem' + str(j)] for j in
        range(MAX_LIST_COUNT) if 'TopRankItem' + str(j) in feature['Property'][
            'Detail']]  # TopRankItem1, TopRankItem2 ... のキーをリストに。
    restaurant_info['CassetteOwnerLogoImage'] = feature['Property']['Detail'].get(
        'CassetteOwnerLogoImage')
    if len(feature['Property']['Genre']) > 0:
        restaurant_info['Category'] = feature['Property']['Genre'][0]['Name']
    restaurant_info['UrlWeb'] = "https://loco.yahoo.co.jp/place/" + restaurant_id
    restaurant_info['UrlMap'] = "https://map.yahoo.co.jp/route/walk?from=" + str(
        fetch_group.address) + "&to=" + restaurant_info['Address']
    restaurant_info['ReviewRating'], restaurant_info[
        'ReviewRatingFloat'] = self.get_review_rating(
        restaurant_id) if access_flag == "get" else "", 0
    restaurant_info['BusinessHour'] = (
        feature['Property']['Detail'].get('BusinessHour')).replace('<br>', '\n').replace(
        '<br />', '') if feature['Property']['Detail'].get(
        'BusinessHour') is not None else ""
    restaurant_info['Genre'] = feature['Property']['Genre']
    restaurant_info['Lon'], restaurant_info['Lat'] = tuple(
        [float(x) for x in feature['Geometry']['Coordinates'].split(',')])

    # Images : 画像をリストにする
    lead_image = [feature['Property']['LeadImage']] if 'LeadImage' in feature[
        'Property'] else (
        [feature['Property']['Detail']['Image1']] if 'Image1' in feature['Property'][
            'Detail'] else [])  # リードイメージがある時はImage1を出力しない。
    image_n = [feature['Property']['Detail']['Image' + str(j)] for j in
               range(2, MAX_LIST_COUNT) if 'Image' + str(j) in feature['Property'][
                   'Detail']]  # Image1, Image2 ... のキーをリストに。
    persistency_image_n = [feature['Property']['Detail']['PersistencyImage' + str(j)] for
                           j in range(MAX_LIST_COUNT) if
                           'PersistencyImage' + str(j) in feature['Property'][
                               'Detail']]  # PersistencyImage1, PersistencyImage2 ... のキーをリストに。
    restaurant_info['Images'] = list(
        dict.fromkeys(lead_image + image_n + persistency_image_n))

    # restaurant_info["Image_references"] = calc_info.get_google_images(
    #     feature['Name']) if access_flag=="xxx" else [] #google
    # # apiの画像のreferenceを保存
    # restaurant_info["ImageFiles"] = calc_info.create_image(
    #     restaurant_info) if access_flag=="xxx" else [] #1枚の画像のURLを保存
    # if len(restaurant_info["Images"]) == 0:
    #     no_image_url = "http://drive.google.com/uc?export=view&id=1mUBPWv3kL-1u2K8LFe8p_tL3DoU65FJn"
    #     restaurant_info["Images"] = [no_image_url, no_image_url]

    return restaurant_info


def get_feature_from_api(self, fetch_group, group_id, search_params,
                         access_flag):
    '''
    Yahoo local search APIで店舗情報(feature)を取得する。

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
    feature_list : [list]
    APIから返ってきたレストラン情報のリスト
    '''

    print(f"get_info_from_api(api_yahoo):{access_flag}")

    # Yahoo local search APIで店舗情報を取得
    local_search_url = 'https://map.yahooapis.jp/search/local/V1/localSearch'
    search_params.update({
        'appid': os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        'output': 'json',
        'gc': '01',
        'detail': 'full'
    })
    try:
        response = requests.get(local_search_url, params=search_params)
        local_search_json = response.json()
    except Exception as e:
        abort(e.code)

    # 検索の該当が無かったとき
    if local_search_json['ResultInfo']['Count'] == 0:
        return []

    feature_list = local_search_json['Feature']
    return feature_list


def search_restaurants_info(self, fetch_group, group_id, search_params):
    access_flag = "search"

    # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
    lunch_time_start = 10  # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
    lunch_time_end = 15
    if 'open' in search_params and search_params['open'] != 'now':
        lunch_or_dinner = 'lunch' if lunch_time_start <= int(
            (search_params['open'].split(','))[1]) < lunch_time_end else 'dinner'
    else:
        now_time = datetime.datetime.now().hour + datetime.datetime.now().minute / 60
        lunch_or_dinner = 'lunch' if lunch_time_start <= now_time < lunch_time_end else 'dinner'

    # YahooAPIからレストランのfeatureのリストを取得する
    feature_list = self.get_feature_from_api(
        fetch_group,
        group_id,
        search_params
        , access_flag
    )
    print(f"search_restaurants_info: result: {len(feature_list)} items")

    # feature_listをクライアントアプリに送るjsonに変換する
    restaurants_info = list(map(lambda feature:
                                self.feature_to_info(
                                    fetch_group,
                                    group_id,
                                    lunch_or_dinner,
                                    feature,
                                    access_flag)
                                , feature_list))

    return restaurants_info


def get_restaurants_info(self, fetch_group, group_id, restaurant_ids):
    access_flag = "get"

    search_params = {'uid': ','.join(restaurant_ids)}
    print(f"get_restaurants_info: get {len(restaurant_ids)} items")
    # YahooAPIからレストランの情報を取得する
    feature_list = self.get_feature_from_api(
        fetch_group,
        group_id,
        search_params
        , access_flag
    )
    print(f"get_restaurants_info: get {len(feature_list)} items")

    # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
    lunch_time_start = 10  # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
    lunch_time_end = 15
    if 'open' in search_params and search_params['open'] != 'now':
        lunch_or_dinner = 'lunch' if lunch_time_start <= int(
            (search_params['open'].split(','))[1]) < lunch_time_end else 'dinner'
    else:
        now_time = datetime.datetime.now().hour + datetime.datetime.now().minute / 60
        lunch_or_dinner = 'lunch' if lunch_time_start <= now_time < lunch_time_end else 'dinner'

    # feature_listをクライアントアプリに送るjsonに変換する
    restaurants_info = list(map(lambda feature:
                                self.feature_to_info(
                                    fetch_group,
                                    group_id,
                                    lunch_or_dinner,
                                    feature,
                                    access_flag)
                                , feature_list))

    # #各お店のオススメ度を追加(相対評価)
    # restaurants_info = calc_info.calc_recommend_score(fetch_group, group_id, restaurants_info)
    return restaurants_info


def get_review_rating_string(self, review_rating):
    '''
    口コミを文字列で返す
    '''
    review_rating = float(review_rating)
    review_rating_int = int(review_rating + 0.5)
    review_rating_star = '★' * review_rating_int + '☆' * (5 - review_rating_int)
    return review_rating_star + '    ' + ('%.1f' % review_rating)


def get_place_details(self, fetch_group, group_id, restaurant_ids):
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    lunch_or_dinner = None
    restaurants_info = []
    for r_id in restaurant_ids:
        search_params = {
            'key': os.environ['GOOGLE_API_KEY'],
            'place_id': r_id,
        }  # 検索クエリの設定(詳しくはPlace Search APIのドキュメント参照)
        try:
            response = requests.get(url=url, params=search_params)
            local_search_json = response.json()  # レスポンスのjsonをdict型にする
        except Exception as e:
            abort(e.code)
        feature = local_search_json['result']
        restaurant_info = self.feature_to_info(fetch_group, group_id, feature)
        restaurants_info.append(restaurant_info)

    # 各お店のオススメ度を追加(相対評価)
    # restaurants_info = calc_info.calc_recommend_score(fetch_group, group_id, restaurants_info)
    return restaurants_info


# 写真の参照から写真のURLのリストを取得
def get_place_photo_urls(self, photo_references, photo_nums=3):
    """
    photo_referenceからお店の写真を取得して表示する
    :param key: API key
    :param photo_references: 写真参照キーのリスト
    :return:photos: Imageオブジェクトのリスト
    """
    url = 'https://maps.googleapis.com/maps/api/place/photo'
    maxheight = 400
    image_urls = []  # お店の写真のImageオブジェクトのリスト
    # photo_referenceごとにAPIを叩いて画像を取得
    for photo_ref in photo_references:
        # Place Photos
        # params = {
        #     'key': os.environ['GOOGLE_API_KEY'],
        #     'photoreference': photo_ref,
        #     'maxheight': maxheight,
        # }
        # response = requests.get(url=url, params=params)

        # 返ってきたバイナリをImageオブジェクトに変換
        # photo = Image.open(BytesIO(response.content))
        photo_reference_url = url + f"?maxwidth={maxheight}&photo_reference={photo_ref}&key={os.environ['GOOGLE_API_KEY']}"
        image_urls.append(photo_reference_url)
        # image_urls.append("")
        # photos.append(photo)
        if len(image_urls) >= photo_nums:  # 指定枚数返す
            return image_urls
    return image_urls


def google_feature_to_info(self, fetch_group, group_id, feature):
    '''
    Google APIで取得した店舗情報(feature)を、クライアントに送信するjsonの形式に変換する。

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


def get_info_from_nearby_search_api(self, fetch_group, group_id, search_params):
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

    lunch_time_start = 10  # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
    lunch_time_end = 15

    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'  # 緯度経度と半径からお店を取得
    search_params.update({
        'key': os.environ['GOOGLE_API_KEY'],
        'output': 'json',
        'type': 'restaurant'
    })  # 検索クエリの設定(詳しくはPlace Search APIのドキュメント参照)
    print("================================")
    print(f"google nearby search:")
    print(search_params)
    print("================================")
    try:
        response = requests.get(url=url, params=search_params)
        local_search_json = response.json()  # レスポンスのjsonをdict型にする
    except Exception as e:
        abort(e.code)

    # 検索の該当が無かったとき
    if len(local_search_json['results']) == 0:
        print("non nearby search")
        return {}, []

    # apiで受け取ったjsonをクライアントアプリに送るjsonに変換する
    restaurants_info = []
    for i, feature in enumerate(local_search_json['results']):  # 最大20件まで取れる
        restaurant_info = self.feature_to_info(fetch_group, group_id, feature)
        restaurants_info.append(restaurant_info)

    # 各お店のオススメ度を追加(相対評価)
    # restaurants_info = calc_info.calc_recommend_score(fetch_group, group_id, restaurants_info)
    return restaurants_info
