import requests
import os
import datetime
from geopy.distance import great_circle
from app import calc_info
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History
from abc import ABCMeta, abstractmethod

'''

APIで店舗情報を取得する．
========
search_restaurant_infoとget_restaurant_infoが最初に呼ばれる．

# 新しいAPIの記述
 - ApiFunctionsクラスを継承して記述してください．
 - ApiFunctionsYahooクラスを参考にしてください
 - search_restaurant_info関数とget_restaurant_info関数に作ったクラスを追加してください．

 # 主な変数
search_params : dict
    Yahoo Local Search API の検索クエリと一緒
restaurants_info = result_json: dict
    ユーザにレスポンスするjson

'''

# ============================================================================================================
# ApiFunctionsクラス関連


class ApiFunctions(metaclass=ABCMeta):

    @abstractmethod
    def search_restaurants_info(self, fetch_group, group_id, search_params):
        '''
        レコメンドするために条件に合う店を取ってくる

        Parameters
        ----------------
        fetch_group : 
            データベースのグループ情報
        group_id: int
            グループID
        search_params : dict
            検索条件
        
        Returns
        ----------------
        result_json : dict
            レスポンスするレストラン情報を返す。
        '''
        pass

    @abstractmethod
    def get_restaurants_info(self, fetch_group, group_id, restaurant_ids):
        '''
        restaurant_idsのお店をユーザに返す

        Parameters
        ----------------
        fetch_group : 
            データベースのグループ情報
        group_id: int
            グループID
        restaurant_ids : [string]
            restaurant_idのリスト
        
        Returns
        ----------------
        result_json : dict
            レスポンスするレストラン情報を返す。
        '''
        pass


class ApiFunctionsYahoo(ApiFunctions):


    def get_review(self, uid):
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
            return {'ResultInfo':{'Count':0}}
            
        return response


    def get_review_rating(self, uid):
        response = self.get_review(uid)
        if response['ResultInfo']['Count'] == 0 : return ''
        review_rating = sum([f['Property']['Comment']['Rating'] for f in response["Feature"]]) / response['ResultInfo']['Count']
        review_rating_int = int(review_rating + 0.5)
        review_rating_star = '★' * review_rating_int + '☆' * (5-review_rating_int)
        return review_rating_star + '    ' + ('%.1f' % review_rating)


    def get_restaurant_info(self, fetch_group, group_id, lunch_or_dinner, feature):
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
        MAX_LIST_COUNT = 10

        restaurant_info = {}
        restaurant_id = feature['Property']['Uid']
        restaurant_info['Restaurant_id'] = restaurant_id
        restaurant_info['Name'] = feature['Name']
        restaurant_info['Address'] = feature['Property']['Address']
        restaurant_info["distance_float"] = great_circle((fetch_group.lat, fetch_group.lon), tuple(reversed([float(x) for x in feature['Geometry']['Coordinates'].split(',')]))).m #距離 メートル float
        restaurant_info['Distance'] = calc_info.distance_display(great_circle((fetch_group.lat, fetch_group.lon), tuple(reversed([float(x) for x in feature['Geometry']['Coordinates'].split(',')]))).m) # 緯度・経度から距離を計算 str
        restaurant_info['CatchCopy'] = feature['Property'].get('CatchCopy')
        restaurant_info['Price'] = feature['Property']['Detail']['LunchPrice'] if lunch_or_dinner == 'lunch' and feature['Property']['Detail'].get('LunchFlag') == True else feature['Property']['Detail'].get('DinnerPrice')
        restaurant_info['LunchPrice'] = feature['Property']['Detail'].get('LunchPrice')
        restaurant_info['DinnerPrice'] = feature['Property']['Detail'].get('DinnerPrice')
        restaurant_info['TopRankItem'] = [feature['Property']['Detail']['TopRankItem'+str(j)] for j in range(MAX_LIST_COUNT) if 'TopRankItem'+str(j) in feature['Property']['Detail']] # TopRankItem1, TopRankItem2 ... のキーをリストに。
        restaurant_info['CassetteOwnerLogoImage'] = feature['Property']['Detail'].get('CassetteOwnerLogoImage')
        restaurant_info['Category'] = feature['Property']['Genre'][0]['Name']
        restaurant_info['UrlYahooLoco'] = "https://loco.yahoo.co.jp/place/" + restaurant_id
        restaurant_info['UrlYahooMap'] = "https://map.yahoo.co.jp/route/walk?from=" + str(fetch_group.address) + "&to=" + restaurant_info['Address']
        restaurant_info['ReviewRating'] = self.get_review_rating(restaurant_id)
        restaurant_info['VotesLike'] = session.query(History).filter(History.group==group_id, History.restaurant==restaurant_id, History.feeling==True).count()
        restaurant_info['VotesAll'] = session.query(History).filter(History.group==group_id, History.restaurant==restaurant_id, History.feeling is not None).count()
        restaurant_info['BusinessHour'] = (feature['Property']['Detail'].get('BusinessHour')).replace('<br>', '\n').replace('<br />', '')
        restaurant_info['Genre'] = feature['Property']['Genre']
        restaurant_info['NumberOfParticipants'] = str(session.query(Belong).filter(Belong.group==group_id).count())

        # Images : 画像をリストにする
        lead_image = [feature['Property']['LeadImage']] if 'LeadImage' in feature['Property'] else ([feature['Property']['Detail']['Image1']] if 'Image1' in feature['Property']['Detail'] else []) # リードイメージがある時はImage1を出力しない。
        image_n = [feature['Property']['Detail']['Image'+str(j)] for j in range(2,MAX_LIST_COUNT) if 'Image'+str(j) in feature['Property']['Detail']] # Image1, Image2 ... のキーをリストに。
        persistency_image_n = [feature['Property']['Detail']['PersistencyImage'+str(j)] for j in range(MAX_LIST_COUNT) if 'PersistencyImage'+str(j) in feature['Property']['Detail']] # PersistencyImage1, PersistencyImage2 ... のキーをリストに。
        restaurant_info['Images'] = list(dict.fromkeys(lead_image + image_n + persistency_image_n))
        if len(restaurant_info["Images"]) == 0:
            no_image_url = "http://drive.google.com/uc?export=view&id=1mUBPWv3kL-1u2K8LFe8p_tL3DoU65FJn"
            restaurant_info["Images"] = [no_image_url, no_image_url]
        
        return restaurant_info


    def get_info_from_api(self, fetch_group, group_id, search_params):
        '''
        Yahoo local search APIで店舗情報(feature)を取得する。
        
        Parameters
        ----------------
        fetch_group : 
            データベースのグループ情報
        group_id : string
            groupID
        search_params : dictionary
            Yahoo local search APIに送信するクエリ
        
        Returns
        ----------------
        restaurant_info : string
            レスポンスするレストラン情報をjson形式で返す。
        '''

        lunch_time_start = 10 # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
        lunch_time_end = 15

        # Yahoo local search APIで店舗情報を取得
        local_search_url = 'https://map.yahooapis.jp/search/local/V1/localSearch'
        search_params.update({
            'appid': os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
            'output': 'json',
            'detail': 'full'
        })
        try:
            response = requests.get(local_search_url, params=search_params)
            local_search_json = response.json()
        except Exception as e:
            abort(e.code)
            
        # 検索の該当が無かったとき
        if local_search_json['ResultInfo']['Count'] == 0:
            return {}, []

        # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
        if 'open' in search_params and search_params['open'] != 'now':
            lunch_or_dinner = 'lunch' if lunch_time_start <= int((search_params['open'].split(','))[1]) < lunch_time_end else 'dinner'
        else:
            now_time = datetime.datetime.now().hour + datetime.datetime.now().minute / 60
            lunch_or_dinner = 'lunch' if lunch_time_start <= now_time < lunch_time_end else 'dinner'

        # Yahoo local search apiで受け取ったjsonをクライアントアプリに送るjsonに変換する
        result_json = []
        for i,feature in enumerate(local_search_json['Feature']):
            result_json.append(self.get_restaurant_info(fetch_group, group_id, lunch_or_dinner, feature))
            
        #各お店のオススメ度を追加(相対評価)
        result_json = calc_info.calc_recommend_score(fetch_group, group_id,result_json)
        return local_search_json, result_json


    def search_restaurants_info(self, fetch_group, group_id, search_params):
        local_search_json, result_json = self.get_info_from_api(fetch_group, group_id, search_params)
        return result_json

    def get_restaurants_info(self, fetch_group, group_id, restaurant_ids):
        search_params = { 'uid': ','.join(restaurant_ids) }
        local_search_json, result_json = self.get_info_from_api(fetch_group, group_id, search_params)
        return result_json




class ApiFunctionsGoogle(ApiFunctions):

    def search_restaurants_info(self, fetch_group, group_id, search_params):
        # TODO
        pass

    def get_restaurants_info(self, fetch_group, group_id, restaurant_ids):
        # TODO
        pass



class ApiFunctionsHotpepper (ApiFunctions):

    def search_restaurants_info(self, fetch_group, group_id, search_params):
        # TODO
        pass

    def get_restaurants_info(self, fetch_group, group_id, restaurant_ids):
        # TODO
        pass


# ============================================================================================================
# api_functions.pyで最初に呼ばれる


def search_restaurants_info(fetch_group, group_id, search_params):
    '''
    レコメンドするために条件に合う店を取ってくる

    Parameters
    ----------------
    fetch_group : 
        データベースのグループ情報
    group_id: int
        グループID
    search_params : dict
        検索条件
    
    Returns
    ----------------
    restaurants_info : dict
        レスポンスするレストラン情報を返す。
    '''
    
    api_f = ApiFunctionsYahoo() # TODO

    return api_f.search_restaurants_info(fetch_group, group_id, search_params)


def get_restaurants_info(fetch_group, group_id, restaurant_ids):
    '''
    restaurant_idsのお店をユーザに返す

    Parameters
    ----------------
    fetch_group : 
        データベースのグループ情報
    group_id: int
        グループID
    restaurant_ids : [string]
        restaurant_idのリスト
    
    Returns
    ----------------
    restaurants_info : dict
        レスポンスするレストラン情報を返す。
    '''

    api_f = ApiFunctionsYahoo() # TODO

    restaurant_ids_del_none = [x for x in restaurant_ids if x]
    return api_f.get_restaurants_info(fetch_group, group_id, restaurant_ids_del_none)

# ============================================================================================================


def get_lat_lon_address(query):
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
        address = response["Feature"][0]["Property"]["Address"]
    except:
        # Yahoo!本社の座標
        lon = 139.73284
        lat = 35.68001 
        address = "東京都千代田区紀尾井町1-3 東京ガ-デンテラス紀尾井町 紀尾井タワ-"
        
    return lat, lon, address
