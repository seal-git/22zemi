import requests
import os
import datetime
from geopy.distance import great_circle


def get_restaurant_info_from_local_search_params(coordinates, address, local_search_params):
    '''
    Yahoo local search APIで取得した店舗情報(feature)を、クライアントに送信するjsonの形式に変換する。
    
    Parameters
    ----------------
    coordinates : (int, int)
        (緯度, 経度)のタプル
    address : string
        住所
    local_search_params : dictionary
        Yahoo local search APIに送信するクエリ
    
    Returns
    ----------------
    restaurant_info : string
        レスポンスするレストラン情報をjson形式で返す。
    '''
    
    MAX_LIST_COUNT = 10
    lunch_time_start = 10 # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
    lunch_time_end = 15

    # Yahoo local search APIで店舗情報を取得
    local_search_url = 'https://map.yahooapis.jp/search/local/V1/localSearch?'
    local_search_params.update({
        'appid': os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        'output': 'json',
        'detail': 'full'
    })
    response = requests.get(local_search_url, params=local_search_params)
    local_search_json = response.json()

    # 検索の該当が無かったとき
    if local_search_json['ResultInfo']['Count'] == 0:
        return "[]"

     # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
    now_time = datetime.datetime.now().hour + datetime.datetime.now().minute / 60
    lunch_or_dinner = 'lunch' if lunch_time_start <= now_time and now_time < lunch_time_end else 'dinner'

    # Yahoo local search apiで受け取ったjsonをクライアントアプリに送るjsonに変換する
    result_json = []
    for i,feature in enumerate(local_search_json['Feature']):
        result_json.append({})
        result_json[i]['Restaurant_id'] = feature['Property']['Uid']
        result_json[i]['Name'] = feature['Name']
        result_json[i]['Address'] = feature['Property']['Address']
        result_json[i]['Distance'] = great_circle(coordinates, tuple(reversed([float(x) for x in feature['Geometry']['Coordinates'].split(',')]))).m # 緯度・経度から距離を計算
        result_json[i]['CatchCopy'] = feature['Property'].get('CatchCopy')
        result_json[i]['Price'] = feature['Property']['Detail']['LunchPrice'] if lunch_or_dinner == 'lunch' and feature['Property']['Detail'].get('LunchFlag') == True else feature['Property']['Detail'].get('DinnerPrice')
        result_json[i]['TopRankItem'] = [feature['Property']['Detail']['TopRankItem'+str(j)] for j in range(MAX_LIST_COUNT) if 'TopRankItem'+str(j) in feature['Property']['Detail']] # TopRankItem1, TopRankItem2 ... のキーをリストに。
        result_json[i]['CassetteOwnerLogoImage'] = feature['Property']['Detail'].get('CassetteOwnerLogoImage')
        result_json[i]['Category'] = ','.join(feature['Category'][0].split(",")[-2:-1]) if len(feature['Category']) != 0 else ''
        result_json[i]['UrlYahooLoco'] = "https://loco.yahoo.co.jp/place/" + result_json[i]['Restaurant_id']
        result_json[i]['UrlYahooMap'] = "https://map.yahoo.co.jp/route/walk?from=" + address + "&to=" + result_json[i]['Address']
        result_json[i]['ReviewRating'] = get_review_rating(feature['Property']['Uid'])

        lead_image = [feature['Property']['LeadImage']] if 'LeadImage' in feature['Property'] else []
        image_n = [feature['Property']['Detail']['Image'+str(j)] for j in range(MAX_LIST_COUNT) if 'Image'+str(j) in feature['Property']['Detail']] # Image1, Image2 ... のキーをリストに。
        persistency_image_n = [feature['Property']['Detail']['PersistencyImage'+str(j)] for j in range(MAX_LIST_COUNT) if 'PersistencyImage'+str(j) in feature['Property']['Detail']] # PersistencyImage1, PersistencyImage2 ... のキーをリストに。
        result_json[i]['Images'] = lead_image + image_n + persistency_image_n

    return local_search_json, result_json


def get_lat_lon(query):
    '''
    緯度，経度をfloatで返す関数

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
    
    例外処理
    ----------------
    不適切なqueryを入力した場合，Yahoo!本社の座標を返す
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
    except:
        # Yahoo!本社の座標
        lon = 139.73284
        lat = 35.68001 
        
    return lat, lon


def get_review(uid):
    '''
    口コミを見ます
    '''
    review_api_url = 'https://map.yahooapis.jp/olp/v1/review/' + uid
    params = {
        "appid": os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        "output": "json",
        "results": "100"
    }
    try:
        response = requests.get(review_api_url, params=params)
        response = response.json()
    except:
        return {}
        
    return response

def get_review_rating(uid):
    response = get_review(uid)
    if response['ResultInfo']['Count'] == 0 : return -1
    return sum([f['Property']['Comment']['Rating'] for f in response["Feature"]]) / response['ResultInfo']['Count']

