import requests
import os
import datetime
from app import database_functions, calc_info
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from app.internal_info import *
from abc import ABCMeta, abstractmethod
from flask import abort
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
        if response['ResultInfo']['Count'] == 0 : return '', 0
        review_rating = sum([f['Property']['Comment']['Rating'] for f in response["Feature"]]) / response['ResultInfo']['Count']
        review_rating_int = int(review_rating + 0.5)
        review_rating_star = '★' * review_rating_int + '☆' * (5-review_rating_int)
        return review_rating_star + '    ' + ('%.1f' % review_rating), review_rating


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
        
        if access_flag=='get': print(f"feature_to_info(api_yahoo):{access_flag}")

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
        if len(feature['Property']['Genre'])>0:
            restaurant_info['Category'] = feature['Property']['Genre'][0]['Name']
        restaurant_info['UrlWeb'] = "https://loco.yahoo.co.jp/place/" + restaurant_id
        restaurant_info['UrlMap'] = "https://map.yahoo.co.jp/route/walk?from=" + str(fetch_group.address) + "&to=" + restaurant_info['Address']
        restaurant_info['ReviewRating'], restaurant_info['ReviewRatingFloat'] = self.get_review_rating(restaurant_id) if access_flag == "get" else "", 0
        restaurant_info['BusinessHour'] = (feature['Property']['Detail'].get('BusinessHour')).replace('<br>', '\n').replace('<br />', '') if feature['Property']['Detail'].get('BusinessHour') is not None else ""
        restaurant_info['Genre'] = feature['Property']['Genre']
        restaurant_info['Lon'], restaurant_info['Lat'] = tuple([float(x) for x in feature['Geometry']['Coordinates'].split(',')])

        
        # Images : 画像をリストにする
        lead_image = [feature['Property']['LeadImage']] if 'LeadImage' in feature['Property'] else ([feature['Property']['Detail']['Image1']] if 'Image1' in feature['Property']['Detail'] else []) # リードイメージがある時はImage1を出力しない。
        image_n = [feature['Property']['Detail']['Image'+str(j)] for j in range(2,MAX_LIST_COUNT) if 'Image'+str(j) in feature['Property']['Detail']] # Image1, Image2 ... のキーをリストに。
        persistency_image_n = [feature['Property']['Detail']['PersistencyImage'+str(j)] for j in range(MAX_LIST_COUNT) if 'PersistencyImage'+str(j) in feature['Property']['Detail']] # PersistencyImage1, PersistencyImage2 ... のキーをリストに。
        restaurant_info['Images'] = list(dict.fromkeys(lead_image + image_n + persistency_image_n))

        restaurant_info["Image_references"] = calc_info.get_google_images(
            feature['Name']) if access_flag=="xxx" else [] #google
        # apiの画像のreferenceを保存
        restaurant_info["ImageFiles"] = calc_info.create_image(
            restaurant_info) if access_flag=="xxx" else [] #1枚の画像のURLを保存
        if len(restaurant_info["Images"]) == 0:
            no_image_url = "http://drive.google.com/uc?export=view&id=1mUBPWv3kL-1u2K8LFe8p_tL3DoU65FJn"
            restaurant_info["Images"] = [no_image_url, no_image_url]
        
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
        lunch_time_start = 10 # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
        lunch_time_end = 15
        if 'open' in search_params and search_params['open'] != 'now':
            lunch_or_dinner = 'lunch' if lunch_time_start <= int((search_params['open'].split(','))[1]) < lunch_time_end else 'dinner'
        else:
            now_time = datetime.datetime.now().hour + datetime.datetime.now().minute / 60
            lunch_or_dinner = 'lunch' if lunch_time_start <= now_time < lunch_time_end else 'dinner'

        #YahooAPIからレストランのfeatureのリストを取得する
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

        search_params = { 'uid': ','.join(restaurant_ids) }
        print(f"get_restaurants_info: get {len(restaurant_ids)} items")
        #YahooAPIからレストランの情報を取得する
        feature_list = self.get_feature_from_api(
            fetch_group,
            group_id,
            search_params
            , access_flag
        )
        print(f"get_restaurants_info: get {len(feature_list)} items")

        # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
        lunch_time_start = 10 # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
        lunch_time_end = 15
        if 'open' in search_params and search_params['open'] != 'now':
            lunch_or_dinner = 'lunch' if lunch_time_start <= int((search_params['open'].split(','))[1]) < lunch_time_end else 'dinner'
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

        #各お店のオススメ度を追加(相対評価)
        restaurants_info = calc_info.calc_recommend_score(fetch_group, group_id, restaurants_info)
        return restaurants_info

class ApiFunctionsGoogle(ApiFunctions):


    def get_review_rating_string(self, review_rating):
        '''
        口コミを文字列で返す
        '''
        review_rating = float(review_rating)
        review_rating_int = int(review_rating + 0.5)
        review_rating_star = '★' * review_rating_int + '☆' * (5-review_rating_int)
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
            
        #各お店のオススメ度を追加(相対評価)
        restaurants_info = calc_info.calc_recommend_score(fetch_group, group_id, restaurants_info)
        return restaurants_info

    #写真の参照から写真のURLのリストを取得
    def get_place_photo_urls(self, photo_references, photo_nums=3):
        """
        photo_referenceからお店の写真を取得して表示する
        :param key: API key
        :param photo_references: 写真参照キーのリスト
        :return:photos: Imageオブジェクトのリスト
        """
        url = 'https://maps.googleapis.com/maps/api/place/photo'
        maxheight = 400
        image_urls = [] # お店の写真のImageオブジェクトのリスト
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
            #photo = Image.open(BytesIO(response.content))
            photo_reference_url = url + f"?maxwidth={maxheight}&photo_reference={photo_ref}&key={os.environ['GOOGLE_API_KEY']}"
            image_urls.append(photo_reference_url)
            #image_urls.append("")
            #photos.append(photo)
            if len(image_urls) >= photo_nums: #指定枚数返す
                return image_urls
        return image_urls

    def feature_to_info(self, fetch_group, group_id, feature):
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
        restaurant_info['Address'] = feature['formatted_address'] if 'formatted_address' in feature.keys() else ""
        restaurant_info['CatchCopy'] = ""
        restaurant_info['Price'] = feature['plus_code']['price_level'] if 'price_level' in feature['plus_code'].keys() else 0
        restaurant_info['LunchPrice'] = feature['plus_code']['price_level'] if 'price_level' in feature['plus_code'].keys() else 0
        restaurant_info['DinnerPrice'] = feature['plus_code']['price_level'] if 'price_level' in feature['plus_code'].keys() else 0
        restaurant_info['TopRankItem'] = [] #[feature['Property']['Detail']['TopRankItem'+str(j)] for j in range(MAX_LIST_COUNT) if 'TopRankItem'+str(j) in feature['Property']['Detail']] # TopRankItem1, TopRankItem2 ... のキーをリストに。
        restaurant_info['CassetteOwnerLogoImage'] = feature['icon']
        restaurant_info['Category'] = feature['types'][0]
        restaurant_info['UrlWeb'] = feature['website'] if 'website' in feature.keys() else ""
        restaurant_info['UrlMap'] = feature['url'] if 'url' in feature.keys() else ""
        restaurant_info['ReviewRating'] = self.get_review_rating_string(feature['rating']) if 'rating' in feature.keys() else ""
        restaurant_info['ReviewRatingFloat'] = float(feature['rating'])
        restaurant_info['BusinessHour'] = feature['opening_hours']['weekday_text'] if ('opening_hours' in feature.keys()) and ('weekday_text' in feature['opening_hours'].keys()) else "unknown"
        restaurant_info['Genre'] = [{'Code': '0', 'Name': 'UnKnown'}]
        #[{'Code': '0110005', 'Name': 'ビアホール'}]この形式にしたい
        restaurant_info['Lat'], restaurant_info['Lon'] = feature['geometry']['location'].values()
        
        # Images : 画像をリストにする
        photo_references = [photo['photo_reference'] for photo in feature['photos']] #photo_referenceを複数取得
        photo_nums = 3 #画像のURL数
        restaurant_info['ImageFiles'] = calc_info.create_image(restaurant_info)
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

        lunch_time_start = 10 # 現在時刻でランチかディナーか決定する。価格表示に使用している。今のところ検索には使用していない。
        lunch_time_end = 15

        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json' #緯度経度と半径からお店を取得
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
        for i,feature in enumerate(local_search_json['results']): #最大20件まで取れる
            restaurant_info = self.feature_to_info(fetch_group, group_id, feature)
            restaurants_info.append(restaurant_info)
            
        #各お店のオススメ度を追加(相対評価)
        restaurants_info = calc_info.calc_recommend_score(fetch_group, group_id, restaurants_info)
        return restaurants_info

    def search_restaurants_info(self, fetch_group, group_id, search_params):
        restaurants_info = self.get_info_from_nearby_search_api(fetch_group, group_id, search_params)
        return restaurants_info

    def get_restaurants_info(self, fetch_group, group_id, restaurant_ids):
        restaurants_info = self.get_place_details(fetch_group, group_id, restaurant_ids)
        return restaurants_info



class ApiFunctionsHotpepper (ApiFunctions):

    def search_restaurants_info(self, fetch_group, group_id, search_params):
        # TODO
        pass

    def get_restaurants_info(self, fetch_group, group_id, restaurant_ids):
        # TODO
        pass



# ============================================================================================================
# api_functions.pyで最初に呼ばれる


def search_restaurants_info(fetch_group, group_id, user_id, search_params):
    '''
    レコメンドするために条件に合う店を取ってくる
    recommend.pyのRecommend.search()から呼ばれる。

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

    api_method = fetch_group.api_method
    if api_method == "yahoo":
        api_f = ApiFunctionsYahoo()
    elif api_method == "google":
        api_f = ApiFunctionsGoogle()

    # APIで店舗情報を取得
    restaurants_info = api_f.search_restaurants_info(fetch_group, group_id, search_params)

    # データベースに店舗情報を保存
    database_functions.save_restaurants_info(restaurants_info)
    database_functions.save_votes(group_id, restaurants_info)

    # 以前に検索したレストランはデータベースから取得する
    fetch_restaurants = session.query(Restaurant).filter(Vote.group==group_id, Vote.restaurant==Restaurant.id).all() # 未送信のもののみを取得するときはfilterに`Vote.votes_all==-1`を加える
    restaurants_info_from_db = [database_functions.convert_restaurants_info_from_fetch_restaurants(r) for r in fetch_restaurants]
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
    api_method = fetch_group.api_method
    if api_method == "yahoo":
        api_f = ApiFunctionsYahoo()
    elif api_method == "google":
        api_f = ApiFunctionsGoogle() 

    # データベースから店舗情報を取得
    print(f"get_restaurants_info: ids: {restaurant_ids}")

    restaurant_ids_del_none = [x for x in restaurant_ids if x is not None]
    restaurants_info = database_functions.load_stable_restaurants_info(restaurant_ids_del_none)

    # データベースにない店舗の情報をAPIで取得
    rest_ids = [rid for rid, r_info in zip(restaurant_ids, restaurants_info) if r_info is None]
    if len(rest_ids)>0:
        rs_info = api_f.get_restaurants_info(fetch_group, group_id, rest_ids)
        for r_info in rs_info:
            restaurants_info[ restaurant_ids_del_none.index(r_info['Restaurant_id']) ] = r_info
    restaurants_info = [r for r in restaurants_info if r is not None] # feelingリクエストで架空のrestaurants_idだったときには、それを除く

    # 投票数と距離を計算
    restaurants_info = calc_info.add_votes_distance(fetch_group, group_id, restaurants_info)

    return restaurants_info
