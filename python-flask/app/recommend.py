from app import api_functions
import json
import os
import random
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History
from sqlalchemy import distinct
from abc import ABCMeta, abstractmethod


'''
レコメンドを行う．
================
recommend_main関数が最初に呼ばれる．

# 新しいレコメンドの記述
Recommendクラスを継承して，レコメンドアルゴリズムを記述してください．
RecommendTemplateクラスの例を参考にしてください．
recommend_mainに作ったクラスを追加してください．
'''

RESULTS_COUNT = 10 # 一回に返す店舗の数
MAX_DISTANCE = 20 # 中心地からの距離 上限20

#カテゴリの類似度が高い物
with open("./data/category_high_sim.json","rb") as f:
    category_high_sim = json.load(f)
#カテゴリの類似度が低い物
with open("./data/category_low_sim.json","rb") as f:
    category_low_sim = json.load(f)
#カテゴリの業種コード3, 検索用
with open("./data/category_code.json","rb") as f:
    category_code = json.load(f)


# ============================================================================================================
# recommendクラス関連

class Recommend(metaclass=ABCMeta):

    @abstractmethod
    def pre_info(self, fetch_group, group_id, user_id):
        '''
        APIを使って候補となる店の情報を取ってくる --> responce_info.pre_result_json

        Parameters
        ----------------
        fetch_group : Group
            データベースのGroupテーブルの情報

        group_id : int

        user_id : int

        Returns
        ----------------
        pre_search_params : dict

        '''
        pass
    
    @abstractmethod
    def responce_info(self, fetch_group, group_id, user_id, pre_result_json):
        '''
        レスポンスでユーザに返す店を決める

        Parameters
        ----------------
        fetch_group : Group
            データベースのGroupテーブルの情報
        
        group_id : int

        user_id : int

        pre_result_json : dict
            pre_infoで取ってきた店の情報

        Returns
        ----------------
        restaurants_list : [restaurant_id]

        '''
        pass


class RecommendTemplate(Recommend):
    '''
    例
    '''
    def pre_info(self, fetch_group, group_id, user_id):
    
        # YahooローカルサーチAPIで検索するクエリ
        local_search_params = {
            # 中心地から1km以内のグルメを検索
            'lat': fetch_group.lat, # 緯度
            'lon': fetch_group.lon, # 経度
            'dist': fetch_group.max_dist, # 中心地点からの距離 # 最大20km
            'gc': '01', # グルメ
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'sort': fetch_group.sort, # hyblid # 評価や距離などを総合してソート
            'start': RESULTS_COUNT * (session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()).request_count, # 表示範囲：開始位置
            'results': RESULTS_COUNT, # 表示範囲：店舗数
        }
        if fetch_group.query is not None:
            local_search_params['query'] = fetch_group.query + ' '
        if fetch_group.genre is not None:
            local_search_params['query'] = fetch_group.genre
        if fetch_group.open_hour is not None:
            local_search_params['open_day'] = str(fetch_group.open_day.day) + ',' + str(fetch_group.open_hour.hour)
        if fetch_group.max_price is not None:
            local_search_params['maxprice'] = fetch_group.max_price
        if fetch_group.min_price is not None:
            local_search_params['minprice'] = fetch_group.min_price
        return local_search_params

    
    def responce_info(self, fetch_group, group_id, user_id, pre_result_json):
        # TODO: 重みを計算
        LOCAL_SEARCH_RESULTS_COUNT = 10
        weight = [0] * LOCAL_SEARCH_RESULTS_COUNT
        for i,result_feature in enumerate(pre_result_json):
            weight[i] = LOCAL_SEARCH_RESULTS_COUNT - i

        # 重み順にソートして出力
        result_json = sorted(zip(weight, pre_result_json), key=lambda x:x[0], reverse=True)
        result_json = [rj[1] for rj in result_json]
        result_json = result_json[request_count * RESULTS_COUNT : (request_count+1) * RESULTS_COUNT]
        return result_json


class RecommendSimple(Recommend):
    def pre_info(self, fetch_group, group_id, user_id):
    
        # YahooローカルサーチAPIで検索するクエリ
        local_search_params = {
            # 中心地から1km以内のグルメを検索
            'lat': fetch_group.lat, # 緯度
            'lon': fetch_group.lon, # 経度
            'dist': fetch_group.max_dist, # 中心地点からの距離 # 最大20km
            'gc': '01', # グルメ
            #'gc': code, #ランダムなジャンル 滅多にお店が取れない
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'sort': fetch_group.sort, # hyblid # 評価や距離などを総合してソート
            'start': RESULTS_COUNT * (session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()).request_count, # 表示範囲：開始位置
            'results': RESULTS_COUNT, # 表示範囲：店舗数
        }
        if fetch_group.query is not None:
            local_search_params['query'] = fetch_group.query + ' '
        if fetch_group.genre is not None:
            local_search_params['query'] = fetch_group.genre
        if fetch_group.open_hour is not None:
            local_search_params['open_day'] = str(fetch_group.open_day.day) + ',' + str(fetch_group.open_hour.hour)
        if fetch_group.max_price is not None:
            local_search_params['maxprice'] = fetch_group.max_price
        if fetch_group.min_price is not None:
            local_search_params['minprice'] = fetch_group.min_price
        return local_search_params


    def responce_info(self, fetch_group, group_id, user_id, pre_result_json):
        result_json = delete_duplicate_result(fetch_group, group_id, user_id, pre_result_json)
        if not fetch_group.max_price is None:
            result_json = get_result_json_price_filter(fetch_group.max_price, result_json)

        return [r['Restaurant_id'] for r in result_json]
    

    def get_result_json_price_filter(self, meanprice, result_json):
        new_result_json = []
        for result in result_json:
            if not result['LunchPrice'] is None:
                if int(result['LunchPrice']) > meanprice:
                    continue

            if not result['DinnerPrice'] is None:
                if int(result['DinnerPrice']) > meanprice:
                    continue

            new_result_json.append(result)

        return new_result_json


    def delete_duplicate_result(self, fetch_group, group_id, user_id, result_json):
        result_json_tmp = []
        for i in range(len(result_json)):
            fetch_history = session.query(History).filter(History.group==group_id, History.user==user_id, History.restaurant==result_json[i]["Restaurant_id"]).first()
            if fetch_history is None:
                result_json_tmp.append(result_json[i])
        return result_json_tmp


class RecommendYahoo(Recommend):
    '''
    レコメンドは Yahoo Local Search に任せる
    '''
    def pre_info(self, fetch_group, group_id, user_id):
    
        # YahooローカルサーチAPIで検索するクエリ
        local_search_params = {
            # 中心地から1km以内のグルメを検索
            'lat': fetch_group.lat, # 緯度
            'lon': fetch_group.lon, # 経度
            'dist': fetch_group.max_dist, # 中心地点からの距離 # 最大20km
            'gc': '01', # グルメ
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'sort': fetch_group.sort, # hyblid # 評価や距離などを総合してソート
            'start': RESULTS_COUNT * (session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()).request_count, # 表示範囲：開始位置
            'results': RESULTS_COUNT, # 表示範囲：店舗数
        }
        if fetch_group.query is not None:
            local_search_params['query'] = fetch_group.query + ' '
        if fetch_group.genre is not None:
            local_search_params['query'] = fetch_group.genre
        if fetch_group.open_hour is not None:
            local_search_params['open_day'] = str(fetch_group.open_day.day) + ',' + str(fetch_group.open_hour.hour)
        if fetch_group.max_price is not None:
            local_search_params['maxprice'] = fetch_group.max_price
        if fetch_group.min_price is not None:
            local_search_params['minprice'] = fetch_group.min_price
        return local_search_params

    
    def responce_info(self, fetch_group, group_id, user_id, pre_result_json):
        return [r['Restaurant_id'] for r in pre_result_json]


class RecommendGenre(Recommend):
    def pre_info(self, fetch_group, group_id, user_id):
        return {}
    
    def responce_info(self, fetch_group, group_id, user_id, pre_result_json):
        return []

    def __TODO(self, fetch_group, group_id, user_id, pre_result_json):
        result_json = get_continued_restaurants(fetch_group, group_id, user_id)
        if len(result_json) != 0:
            return result_json
        else:
            simple_method = random.choice(['rating', 'score', 'hyblid', 'review', 'kana', 'price', 'dist', 'geo', '-rating', '-score', '-hyblid', '-review', '-kana', '-price', '-dist', '-geo'])
            simple_method = 'rating'
            #データがなければsimple
            if len(current_group[group_id]["Restaurants"].keys()) == 0:
                print("start")
                result_json = recommend_simple(fetch_group, group_id, user_id, simple_method)
                return result_json

            else:
                LOCAL_SEARCH_RESULTS_COUNT = 10 # 一回に取得する店舗の数 # RESULTS_COUNTの倍数
            coordinates = current_group[group_id]['Coordinates']
            request_count = current_group[group_id]['Users'][user_id]['RequestCount']
            group_result = current_group[group_id]["Restaurants"]
            restaurant_ids = list(group_result.keys())
            keep_restaurant_ids = []
            through_restaurant_ids = []
            keep_list = [] #[[Like数, 価格, 距離, [ジャンル]],...] ジャンル=[{Name:???, Code:???}, {Name:???, Code:???}] 
            through_list = [] #[[All数, Like数, 価格, 距離,　[ジャンル]],...] 
            for r_id in restaurant_ids:
                if len(group_result[r_id]["Like"]) > 0:
                    keep_restaurant_ids.append(r_id)
                    keep_list.append([ len(group_result[r_id]['Like']), group_result[r_id]['info']['Price'], \
                        group_result[r_id]['info']['distance_float'], group_result[r_id]['info']['Genre'] ] )
                else:
                    through_restaurant_ids.append(r_id)
                    through_list.append([ len(group_result[r_id]['All']), len(group_result[r_id]['Like']), group_result[r_id]['info']['Price'], \
                        group_result[r_id]['info']['distance_float'], group_result[r_id]['info']['Genre'] ] )
            
            #keep or throughの結果からジャンルを決定
            if random.random() <= 0.7:
                recommend_type = "keep"
            else:
                recommend_type = "through"
            print(f"RecommendType:{recommend_type}")

            #keepから 平均価格, 平均距離を算出
            keep_price = 0
            keep_distance = 0
            like_num = 0
            for keep in keep_list:
                like_num += keep[0]
                if keep[1] is not None:
                    keep_price += keep[0] * int(keep[1]) #投票数で重み付け TODO:投票率で重み付？
                keep_distance += keep[0] * keep[2]
            if like_num != 0:
                meanprice = int(keep_price / like_num)
                if meanprice == 0:
                    meanprice = None
                meandistance = round( ((keep_distance / like_num) / 1000), 2)
                if meandistance == 0:
                    meandistance = None
                params = {"dist":meandistance, "price":meanprice}
                print(f"MaxPrice:{meanprice}")
                print(f"Maxdict:{meandistance}")
            else:
                print("No Data : like restaurant")
                result_json = recommend_simple(fetch_group, group_id, user_id, simple_method)
                return result_json

            #keep or throughのジャンルを格納
            if recommend_type == "keep":
                genre = []
                for k in keep_list:
                    for g in k[3]:
                        genre.append(g["Name"])
            elif recommend_type == "through":
                genre = []
                for th in through_list:
                    for g in th[4]:
                        genre.append(g["Name"])
            
            #ジャンルの頻度をカウント
            genre_count = [] #[[カウント数, ジャンル名], ...]
            counted = []
            for c in genre:
                if c not in counted:
                    genre_count.append([genre.count(c), c])
                    counted.append(c)
            genre_count.sort(reverse=True)
            
            #カウントが多いものからレコメンドするジャンルを決定
            code = None
            for c in genre_count:
                high_count_genre = c[1]
                try:
                    if recommend_type == "keep":
                        recommend_genre_list = category_high_sim[high_count_genre]
                    elif recommend_type == "through":
                        recommend_genre_list = category_low_sim[high_count_genre]
                    recommend_genre = random.choice(recommend_genre_list)
                    code = '0' + category_code[recommend_genre]
                    break
                except:
                    continue

            #レコメンドデータがなければ、simpleで検索
            if code is None:
                print("No recommend genre code ")
                result_json = recommend_simple(fetch_group, group_id, user_id, simple_method, params)
                return result_json

            print(f"HighCountGenre:{high_count_genre}")
            print(f"RecommendGenre:{recommend_genre}")
            local_search_params = {
                # 中心地から1km以内のグルメを検索
                'lat': coordinates[0], # 緯度
                'lon': coordinates[1], # 経度
                'dist': meandistance, # 中心地点からの距離 # 最大20km
                'image': 'true', # 画像がある店
                'open': 'now', # 現在開店している店舗
                'start': RESULTS_COUNT * request_count, # 表示範囲：開始位置
                'results': RESULTS_COUNT,
                'maxprice': meanprice,
                'gc': code
            }
            local_search_params.update(current_group[group_id]['FilterParams'])
        
            #local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(current_group[group_id], local_search_params)
            result_json = recommend_simple(fetch_group, group_id, user_id, simple_method, params)
            result_json = delete_duplicate_result(fetch_group, group_id, user_id, result_json)
            result_json = get_result_json_price_filter(meanprice, result_json)

            if len(result_json) == 0:
                print("No Data: recommend genre restaurant")
                result_json = recommend_simple(fetch_group, group_id, user_id, simple_method, params)
                return result_json
            
            print("recommend_genre")
            print(f"data_num {len(result_json)}")
            return result_json


    def recommend_simple(self, current_group, group_id, user_id, recommend_method, params={}):
        '''
        レコメンドは Yahoo Local Search に任せる
        '''
        result_json = get_continued_restaurants(current_group, group_id, user_id)
        if len(result_json) != 0:
            return result_json
        else:
            coordinates = current_group[group_id]['Coordinates']
            request_count = current_group[group_id]['Users'][user_id]['RequestCount']
            code = '0' + random.choice(list(category_code.values()))
            if "dist" in params.keys():
                dist = params["dist"]
            else:
                dist = MAX_DISTANCE
            dist = MAX_DISTANCE #距離固定
            if "price" in params.keys():
                price = params["price"]
            else:
                price = None

            # YahooローカルサーチAPIで検索するクエリ
            local_search_params = {
                # 中心地から1km以内のグルメを検索
                'lat': coordinates[0], # 緯度
                'lon': coordinates[1], # 経度
                'dist': dist, # 中心地点からの距離 # 最大20km
                'gc': '01', # グルメ b
                #'gc': code, #ランダムなジャンル 滅多にお店が取れない
                'image': 'true', # 画像がある店
                'open': 'now', # 現在開店している店舗
                'sort': recommend_method, # hyblid # 評価や距離などを総合してソート
                'start': RESULTS_COUNT * request_count, # 表示範囲：開始位置
                'results': RESULTS_COUNT, # 表示範囲：店舗数
                'maxprice': price
            }
            local_search_params.update(current_group[group_id]['FilterParams'])
            
            # Yahoo local search APIで店舗情報を取得
            local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(current_group[group_id], local_search_params)
            result_json = delete_duplicate_result(current_group, group_id, user_id, result_json)
            if not price is None:
                result_json = get_result_json_price_filter(price, result_json)

            save_result(current_group, group_id, user_id, result_json)
            print("recommend_simple")
            print(f"RecommendMethod:{recommend_method}")
            print(f"data_num {len(result_json)}")
            return result_json


class RecommendWords(Recommend):
    '''
    口コミによるレコメンド
    ReviewRatingが3以上の店舗を返す
    一回のレスポンスで返す店舗数は0~10の間
    '''

    def pre_info(self, fetch_group, group_id, user_id):
        LOCAL_SEARCH_RESULTS_COUNT = 10 # 一回に取得する店舗の数
        coordinates = current_group[group_id]['Coordinates']
        address = current_group[group_id]['Address']
        
        request_count = current_group[group_id]['Users'][user_id]['RequestCount']

        local_search_params = {
            # 中心地から1km以内のグルメを検索
            'lat': fetch_group.lat, # 緯度
            'lon': fetch_group.lon, # 経度
            'dist': fetch_group.max_dist, # 中心地点からの距離 # 最大20km
            'gc': '01', # グルメ
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'sort': 'hybrid', # 評価や距離などを総合してソート
            'start': LOCAL_SEARCH_RESULTS_COUNT * request_count, # 表示範囲：開始位置
            'results': LOCAL_SEARCH_RESULTS_COUNT
        }
        local_search_params.update(current_group[group_id]['FilterParams'])
        return local_search_params
    
    def responce_info(self, fetch_group, group_id, user_id, pre_result_json):

        result_json = sorted(pre_result_json, key=lambda x:x['ReviewRating'], reverse=True)
        stop_index = [i for i, x in enumerate(result_json) if x['ReviewRating'] < 3][0]
        result_json = result_json[:stop_index]
        return result_json


# ============================================================================================================
# Yahoo Local Search テスト用

def local_search_test(fetch_group, group_id, user_id):
    '''
    simpleのYahoo Local Searchの出力を見る
    '''
    coordinates = current_group[group_id]['Coordinates']
    request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    
     # YahooローカルサーチAPIで検索するクエリ
    local_search_params = {
        # 中心地から1km以内のグルメを検索
        'lat': coordinates[0], # 緯度
        'lon': coordinates[1], # 経度
        'dist': MAX_DISTANCE, # 中心地点からの距離 # 最大20km
        'gc': '01', # グルメ
        'image': True, # 画像がある店
        'open': 'now', # 現在開店している店舗
        'sort': 'hybrid', # 評価や距離などを総合してソート
        'start': RESULTS_COUNT * request_count, # 表示範囲：開始位置
        'results': RESULTS_COUNT # 表示範囲：店舗数
    }
    local_search_params.update(current_group[group_id]['FilterParams'])

    # Yahoo local search APIで店舗情報を取得
    local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(current_group[group_id], local_search_params)
    return str(local_search_json)


def local_search_test_URL(fetch_group, group_id, user_id):
    '''
    simpleのYahoo Local Searchの出力を見る
    '''
    coordinates = current_group[group_id]['Coordinates']
    request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    
     # YahooローカルサーチAPIで検索するクエリ
    local_search_params = {
        # 中心地から1km以内のグルメを検索
        'lat': coordinates[0], # 緯度
        'lon': coordinates[1], # 経度
        'dist': MAX_DISTANCE, # 中心地点からの距離 # 最大20km
        'gc': '01', # グルメ
        'image': True, # 画像がある店
        'open': 'now', # 現在開店している店舗
        'sort': 'hybrid', # 評価や距離などを総合してソート
        'start': RESULTS_COUNT * request_count, # 表示範囲：開始位置
        'results': RESULTS_COUNT # 表示範囲：店舗数
    }
    local_search_params.update(current_group[group_id]['FilterParams'])

    # Yahoo local search APIで店舗情報を取得
    local_search_url = 'https://map.yahooapis.jp/search/local/V1/localSearch'
    local_search_params.update({
        'appid': os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        'output': 'json',
        'detail': 'full'
    })
    return local_search_url + '?' + '&'.join([k+'='+str(v) for k,v in local_search_params.items()])



# ============================================================================================================
# result_mainで使う関数など

def save_result(fetch_group, group_id, user_id, result_json, params = {}):
    for i in range(len(result_json)):
        fetch_history = session.query(History).filter(History.group==group_id, History.user==user_id, History.restaurant==result_json[i]["Restaurant_id"]).first()
        if fetch_history is None:
            new_history = History()
            new_history.group = group_id
            new_history.user = user_id
            new_history.restaurant = result_json[i]["Restaurant_id"]
            new_history.feeling = None
            session.add(new_history)
            session.commit()

    if "dist" in params.keys():
        fetch_group.group_distance = params["dist"]
        session.commit()
    # else:
    #     fetch_group.group_distance = None
    if "price" in params.keys():
        fetch_group.group_price = params["price"]
        session.commit()
    # else:
    #     fetch_group.group_price = None


def delete_duplicate_result(fetch_group, group_id, user_id, result_json):
    result_json_tmp = []
    for i in range(len(result_json)):
        fetch_history = session.query(History).filter(History.group==group_id, History.user==user_id, History.restaurant==result_json[i]["Restaurant_id"]).first()
        if fetch_history is None:
            result_json_tmp.append(result_json[i])
    return result_json_tmp


def get_continued_restaurants(fetch_group, group_id, user_id):
    user_num = session.query(History).distinct(History.restaurant).filter(History.group==group_id, History.user==user_id).count()
    restaurant_num = session.query(Hisotry).distinct(History.restaurant).filter(History.group==group_id).count()
    result_json = []
    return_restaurant_ids = []
    if user_num < restaurant_num:
        try:
            return_restaurant_ids = fetch_group[group_id]["RestaurantsOrder"][user_num:user_num+RESULTS_COUNT]
        except:
            return_restaurant_ids = fetch_group[group_id]["RestaurantsOrder"][user_num:]
    for i, r_id in enumerate(return_restaurant_ids):
        result_json.append(fetch_group[group_id]['Restaurants'][r_id]['info'])
    return result_json


def get_result_json_price_filter(meanprice, result_json):
    new_result_json = []
    for result in result_json:
        if not result['LunchPrice'] is None:
            if int(result['LunchPrice']) > meanprice:
                continue

        if not result['DinnerPrice'] is None:
            if int(result['DinnerPrice']) > meanprice:
                continue

        new_result_json.append(result)

    return new_result_json


# ============================================================================================================
# recommend.pyで最初に呼ばれる

def recommend_main(fetch_group, group_id, user_id):
    '''
    Yahoo local search APIで情報を検索し、json形式で情報を返す
    
    Parameters
    ----------------
    fetch_group : dictionary
    group_id : int
    user_id : int
    
    Returns
    ----------------
    restaurant_info : dict
        レスポンスするレストラン情報をjson形式で返す。
    '''
    # ratingは、星の数順にソートします。
    # scoreは、スコア順にソートします。
    # hybridは、口コミ件数や星の数などを重み付けした値の順にソートします。
    # reviewは、口コミ件数にソートします。
    # kanaは、アイウエオ順にソートします。
    # priceは、金額順にソートします。
    # distは、2点間の直線距離順にソートします。（geoより高速です）
    # geoは、球面三角法による2点間の距離順にソートします。
    
    # TODO: レコメンド関数の追加
    recommend_method = fetch_group.recommend_method
    recomm = RecommendSimple()
    if recommend_method in ['rating', 'score', 'hyblid', 'review', 'kana', 'price', 'dist', 'geo', '-rating', '-score', '-hyblid', '-review', '-kana', '-price', '-dist', '-geo']:
        recomm = RecommendSimple()
    elif recommend_method == 'template':
        recomm = RecommendTemplate()
    elif recommend_method == 'review_words':
        recomm = RecommendWords()
    elif recommend_method == 'genre':
        recomm = RecommendGenre()
    elif recommend_method == 'local_search_test':
        return local_search_test(fetch_group, group_id, user_id)
    elif recommend_method == 'local_search_test_URL':
        return local_search_test_URL(fetch_group, group_id, user_id)


    # result_json = get_continued_restaurants(fetch_group, group_id, user_id) # 2回目以降
    # if len(result_json) != 0:
    #     return result_json
    else:
        for i in range(1000):
            pre_search_params = recomm.pre_info(fetch_group, group_id, user_id)
            pre_result_json = api_functions.search_restaurant_info(fetch_group, group_id, pre_search_params)
            restaurants_list = recomm.responce_info(fetch_group, group_id, user_id, pre_result_json)
            result_json = api_functions.get_restaurant_info(fetch_group, group_id, restaurants_list)

            save_result(fetch_group, group_id, user_id, result_json)
            print(f"RecommendMethod:{recommend_method}")
            print(f"data_num {len(result_json)}")
            if len(result_json) >= 1:
                return result_json

