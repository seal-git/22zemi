import requests
import os
import datetime
from app import calc_info
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from abc import ABCMeta, abstractmethod

'''

APIで店舗情報を取得する。
========
search_restaurant_infoとget_restaurant_infoが最初に呼ばれる。

# 新しいAPIの記述
 - ApiFunctionsクラスを継承して記述してください。
 - ApiFunctionsYahooクラスを参考にしてください
 - search_restaurant_info関数とget_restaurant_info関数に作ったクラスを追加してください。

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
        restaurants_info : [dict]
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
        restaurants_info : [dict]
            レスポンスするレストラン情報を返す。
        '''
        pass


class ApiFunctionsYahoo(ApiFunctions):


    def get_review(self, uid):
        '''
        Yahoo APIにアクセスして口コミを見ます
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
        '''
        Yahoo APIにアクセスして口コミを文字列で返す
        '''
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
        restaurant_info['CatchCopy'] = feature['Property'].get('CatchCopy')
        restaurant_info['Price'] = feature['Property']['Detail']['LunchPrice'] if lunch_or_dinner == 'lunch' and feature['Property']['Detail'].get('LunchFlag') == True else feature['Property']['Detail'].get('DinnerPrice')
        restaurant_info['Price'] = int(restaurant_info['Price']) if type(restaurant_info['Price']) is str else restaurant_info['Price']
        restaurant_info['LunchPrice'] = feature['Property']['Detail'].get('LunchPrice')
        restaurant_info['DinnerPrice'] = feature['Property']['Detail'].get('DinnerPrice')
        restaurant_info['TopRankItem'] = [feature['Property']['Detail']['TopRankItem'+str(j)] for j in range(MAX_LIST_COUNT) if 'TopRankItem'+str(j) in feature['Property']['Detail']] # TopRankItem1, TopRankItem2 ... のキーをリストに。
        restaurant_info['CassetteOwnerLogoImage'] = feature['Property']['Detail'].get('CassetteOwnerLogoImage')
        restaurant_info['Category'] = feature['Property']['Genre'][0]['Name']
        restaurant_info['UrlYahooLoco'] = "https://loco.yahoo.co.jp/place/" + restaurant_id
        restaurant_info['UrlYahooMap'] = "https://map.yahoo.co.jp/route/walk?from=" + str(fetch_group.address) + "&to=" + restaurant_info['Address']
        restaurant_info['ReviewRating'] = self.get_review_rating(restaurant_id)
        restaurant_info['BusinessHour'] = (feature['Property']['Detail'].get('BusinessHour')).replace('<br>', '\n').replace('<br />', '')
        restaurant_info['Genre'] = feature['Property']['Genre']
        restaurant_info['Lon'], restaurant_info['Lat'] = tuple([float(x) for x in feature['Geometry']['Coordinates'].split(',')])

        
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
        group_id : int
            groupID
        search_params : dict
            Yahoo local search APIに送信するクエリ
        
        Returns
        ----------------
        restaurants_info : [dict]
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
        restaurants_info = []
        for i,feature in enumerate(local_search_json['Feature']):
            restaurants_info.append(self.get_restaurant_info(fetch_group, group_id, lunch_or_dinner, feature))
            
        #各お店のオススメ度を追加(相対評価)
        restaurants_info = calc_info.calc_recommend_score(fetch_group, group_id, restaurants_info)
        return local_search_json, restaurants_info


    def search_restaurants_info(self, fetch_group, group_id, search_params):
        local_search_json, restaurants_info = self.get_info_from_api(fetch_group, group_id, search_params)
        return restaurants_info

    def get_restaurants_info(self, fetch_group, group_id, restaurant_ids):
        search_params = { 'uid': ','.join(restaurant_ids) }
        local_search_json, restaurants_info = self.get_info_from_api(fetch_group, group_id, search_params)
        return restaurants_info




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


def search_restaurants_info(fetch_group, group_id, user_id, search_params, histories_restaurants):
    '''
    レコメンドするために条件に合う店を取ってくる
    recommend.pyのRecommend.pre_info()から呼ばれる。

    Parameters
    ----------------
    fetch_group : 
        データベースのグループ情報
    group_id : int
    user_id : int
    search_params : dict
        検索条件
    
    Returns
    ----------------
    restaurants_info : [dict]
        レスポンスするレストラン情報を返す。
    '''
    
    api_f = ApiFunctionsYahoo() # TODO

    # restaurant_info内の、stockからstartとresultを求める
    if 'start' not in search_params or 'result' not in search_params:
        start = session.query(Vote.restaurant).filter(Vote.group==group_id).count()
        result = search_params['stock'] + len(histories_restaurants) - start
        search_params.update({'start': start, 'result': result})
    
    # APIで店舗情報を取得
    restaurants_info = api_f.search_restaurants_info(fetch_group, group_id, search_params)

    # 画像を繋げて1枚にする
    for i,r_info in enumerate(restaurants_info):
        restaurants_info[i]['Image'] = calc_info.create_image(r_info)

    # データベースに店舗情報を保存
    calc_info.save_restaurants_info(restaurants_info)
    calc_info.save_votes(group_id, restaurants_info)

    # 以前に検索したレストランはデータベースから取得する
    fetch_restaurants = session.query(Restaurant).filter(Vote.group==group_id, Vote.votes_all==-1, Vote.restaurant==Restaurant.id).all()
    restaurants_info_from_db = [calc_info.convert_restaurants_info_from_fetch_restaurants(r) for r in fetch_restaurants]
    restaurants_list_from_db = [r['Restaurant_id'] for r in restaurants_info_from_db]
    restaurants_info = restaurants_info_from_db + [r for r in restaurants_info if r['Restaurant_id'] not in restaurants_list_from_db]

    # 投票数と距離を計算
    restaurants_info = calc_info.add_votes_distance(fetch_group, group_id, restaurants_info)

    return restaurants_info


def get_restaurants_info(fetch_group, group_id, restaurant_ids):
    '''
    restaurant_idsのお店をユーザに返す
    recommend.pyのRecommend.response_info()から呼ばれる。listリクエストでも呼ばれる。
    restaurants_idsの順序でrestaurants_infoを返す。

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
    restaurants_info : [dict]
        レスポンスするレストラン情報を返す。
    '''

    api_f = ApiFunctionsYahoo() # TODO

    # データベースから店舗情報を取得
    restaurant_ids_del_none = [x for x in restaurant_ids if x is not None]
    restaurants_info = calc_info.load_restaurants_info(restaurant_ids_del_none)

    # データベースにない店舗の情報をAPIで取得
    rest_ids = [rid for rid, r_info in zip(restaurant_ids, restaurants_info) if r_info is None]
    rs_info = api_f.get_restaurants_info(fetch_group, group_id, rest_ids)
    if(len(rest_ids)!=0): print(str(rest_ids), str(rs_info))
    for r_info in rs_info:
        restaurants_info[ restaurant_ids_del_none.index(r_info['Restaurant_id']) ] = r_info
    restaurants_info = [r for r in restaurants_info if r is not None] # feelingリクエストで架空のrestaurants_idだったときには、それを除く
    
    # 画像を繋げて1枚にする
    for i,r_info in enumerate(restaurants_info):
        if 'Image' not in r_info:
            restaurants_info[i]['Image'] = calc_info.create_image(r_info)

    # 投票数と距離を計算
    restaurants_info = calc_info.add_votes_distance(fetch_group, group_id, restaurants_info)

    return restaurants_info
