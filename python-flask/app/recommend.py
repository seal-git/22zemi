from app import api_functions, calc_info
import json
import os
import random
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from sqlalchemy import distinct
from abc import ABCMeta, abstractmethod


'''

レコメンドを行う。
================
recommend_main関数が最初に呼ばれる。

# 主な流れ
1. pre_info関数で候補となる店の情報を取得する。ユーザが指定した検索条件はこの段階で絞りたい。
2. response_info関数でユーザに表示する店を選ぶ。レコメンドアルゴリズムはここに記述したい。

# 新しいレコメンドの記述
 - Recommendクラスを継承して、レコメンドアルゴリズムを記述してください。
 - RecommendTemplateクラスの例を参考にしてください。
 - recommend_mainに作ったクラスを追加してください。

'''

RESULTS_COUNT = 3 # 一回に返す店舗の数
STOCK_COUNT = 100 # APIで取得するデータの数．STOCK_COUNT個の店からRESULTS_COUNT個選ぶ
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
# Recommendクラス関連

class Recommend(metaclass=ABCMeta):

    @abstractmethod
    def pre_info(self, fetch_group, group_id, user_id):
        '''
        APIを使って候補となる店の情報を取ってくる --> response_info.pre_restaurants_info

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
    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info):
        '''
        レスポンスでユーザに返す店を決める
        pre_restaurants_infoをおすすめ順に並び替えて，RESULTS_COUNT個選ぶ

        Parameters
        ----------------
        fetch_group : Group
            データベースのGroupテーブルの情報
        
        group_id : int

        user_id : int

        pre_restaurants_info : [dict]
            pre_infoで取ってきた店の情報
            一度ユーザに送信した店は排除済み


        Returns
        ----------------
        restaurants_ids : [string]

        '''
        pass


class RecommendTemplate(Recommend):
    '''
    例
    '''
    def pre_info(self, fetch_group, group_id, user_id):
        # YahooローカルサーチAPIで検索するクエリ
        pre_search_params = get_search_params_from_fetch_group(fetch_group)
        pre_search_params.update({
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
        })
        return pre_search_params

    
    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info):
        # TODO: 重みを計算
        weight = [0] * len(pre_restaurants_info)
        for i, pre_restaurant_info in enumerate(pre_restaurants_info):
            weight[i] = len(pre_restaurants_info) - i

        # 重み順にソートして出力
        restaurants_info_tuple = sorted(zip(weight, pre_restaurants_info), key=lambda x:x[0], reverse=True)
        restaurants_ids = [rj[1]['Restaurant_id'] for rj in restaurants_info_tuple]
        return restaurants_ids[0 : RESULTS_COUNT]


class RecommendSimple(Recommend):

    def pre_info(self, fetch_group, group_id, user_id):
        # YahooローカルサーチAPIで検索するクエリ
        pre_search_params = get_search_params_from_fetch_group(fetch_group)
        pre_search_params.update({
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'start': RESULTS_COUNT * (session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()).request_count, # 表示範囲：開始位置
            'results': RESULTS_COUNT, # 表示範囲：店舗数
        })
        return pre_search_params


    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info):
        restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info)
        # if fetch_group.max_price is not None: restaurants_info = get_restaurants_info_price_filter(fetch_group.max_price, restaurants_info)
        return [r['Restaurant_id'] for r in restaurants_info]
    

    def get_restaurants_info_price_filter(self, meanprice, restaurants_info):
        new_restaurants_info = []
        for restaurant_info in restaurants_info:
            if restaurant_info['LunchPrice'] is not None:
                if int(restaurant_info['LunchPrice']) > meanprice:
                    continue

            if restaurant_info['DinnerPrice'] is not None:
                if int(restaurant_info['DinnerPrice']) > meanprice:
                    continue

            new_restaurants_info.append(restaurant_info)

        return new_restaurants_info



class RecommendYahoo(Recommend):
    '''
    レコメンドは Yahoo Local Search に任せる
    '''

    def pre_info(self, fetch_group, group_id, user_id):
        # YahooローカルサーチAPIで検索するクエリ
        pre_search_params = get_search_params_from_fetch_group(fetch_group)
        pre_search_params.update({
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'sort': 'hyblid', # 評価や距離などを総合してソート
            'start': RESULTS_COUNT * (session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()).request_count, # 表示範囲：開始位置
            'results': RESULTS_COUNT, # 表示範囲：店舗数
        })
        return pre_search_params

    
    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info):
        # 何もしない
        return [r['Restaurant_id'] for r in pre_restaurants_info]

class RecommendOriginal(Recommend):
    def pre_info(self, fetch_group):
        # YahooローカルサーチAPIで検索するクエリ
        pre_search_params = get_search_params_from_fetch_group(fetch_group)
        pre_search_params.update({
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
        })
        return pre_search_params

    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info):
        voted= [[v.restaurant, v.votes_like, v.votes_all] for v in session.query(Vote).filter(Vote.group==group_id, Vote.votes_all>0).all()]
        if len(voted) == 0:
            return [r['Restaurant_id'] for r in pre_restaurants_info]
        else:
            #keepに関して
            keep_restaurant_ids = [v[0] for v in voted if v[1] > 0]
            if len(keep_restaurant_ids) > 0:
                keep_count = 0
                keep_genre = [] #keepした店のgenre
                keep_genre_count = []
                weight_price = 0
                weight_distance = 0
                keep_restaurants_info = calc_info.load_restaurants_info(keep_restaurant_ids)
                keep_restaurants_info = calc_info.add_votes_distance(fetch_group, group_id, keep_restaurants_info)
                for r in keep_restaurants_info:
                    id = r["Restaurant_id"]
                    votelike = r["VotesLike"]
                    #price処理
                    price = r["Price"]
                    try:
                        weight_price += votelike * price
                    except:
                        pass
                    #distance処理
                    distance = r["distance_float"]
                    weight_distance += votelike * distance
                    #genre処理
                    genre = r["Genre"]
                    for g in genre:
                        if g["Name"] not in keep_genre:
                            keep_genre.append(g["Name"])
                            keep_genre_count.append(votelike)
                        else:
                            keep_genre_count[keep_genre.index(g["Name"])] += votelike
                    #keep数
                    keep_count += votelike

                keep_genre_rank = [[count, genre] for count, genre in zip(keep_genre_count, keep_genre)]
                keep_genre_rank.sort(reverse=True)
                group_price = weight_price / keep_count
                group_distance = weight_distance / keep_count
                fetch_group.group_price = group_price
                fetch_group.group_distance = round((group_distance / 1000))
                session.commit()

            #throughに関して
            through_restaurant_ids = [v[0] for v in voted if v[1] == 0]
            if len(through_restaurant_ids) > 0:
                through_genre = [] #throughした店のgenre
                through_genre_count = []
                through_restaurants_info = calc_info.load_restaurants_info(through_restaurant_ids)
                through_restaurants_info = calc_info.add_votes_distance(fetch_group, group_id, through_restaurants_info)
                for r in through_restaurants_info:
                    id = r["Restaurant_id"]
                    # votelike = r["VotesLike"]
                    # voteall = r["VotesAll"]
                    # votedislike = voteall - votelike
                    #genre処理
                    genre = r["Genre"]
                    for g in genre:
                        if g["Name"] not in through_genre:
                            through_genre.append(g["Name"])
                            #through_genre_count.append(votedislike)
                        # else:
                        #     through_genre_count[keep_genre.index(g["Name"])] += votedislike
                #through_genre_rank = [[count, genre] for count, genre in zip(through_genre_count, through_genre)]
                #through_genre_rank.sort(reverse=True)

            try:
                if len(keep_restaurant_ids) == len(voted):#全部keepなら
                    high_rank_genre = [g[1] for g in keep_genre_rank if g[0]==max(keep_genre_count)]
                    recommend_genre = random.choice(category_high_sim[random.choice(high_rank_genre)])
                    recommend_type = "high_sim"
                else:
                    if random.random() < 0.7:
                        if len(keep_genre) > 0:
                            high_rank_genre = [g[1] for g in keep_genre_rank if g[0]==max(keep_genre_count)]
                            recommend_genre = random.choice(category_high_sim[random.choice(high_rank_genre)])
                            recommend_type = "high_sim"
                        else:#全部throughなら
                            recommend_genre = random.choice(category_low_sim[random.choice(through_genre)])
                            recommend_type = "low_sim"
                    else:
                        recommend_genre = random.choice(category_low_sim[random.choice(through_genre)])
                        recommend_type = "low_sim"
            except:
                recommend_type = "non genre"
                recommend_genre = ""
            
            # 履歴からrecommendするお店を取得
            non_voted_restaurant_ids =[v.restaurant for v in session.query(Vote).filter(Vote.votes_all==-1)]
            recommend_restaurants_info = calc_info.load_restaurants_info(non_voted_restaurant_ids)
            recommend_restaurants_info = calc_info.add_votes_distance(fetch_group, group_id, recommend_restaurants_info)
            restaurants_id_list = []
            for r in recommend_restaurants_info:
                if r["Price"] <= group_price * 2:
                        if r["distance_float"] <= group_distance * 1.5:
                            if recommend_genre != "":#genreがあれば
                                genre = r["Genre"]
                                for g in genre:
                                    if g["Name"] == recommend_genre:
                                        restaurants_id_list.append(r["Restaurant_id"])
                            else:
                                restaurants_id_list.append(r["Restaurant_id"])
            print("===================================")
            print(recommend_type)
            print(recommend_genre)
            print(group_price)
            print(group_distance)
            print(restaurants_id_list)
            print("===================================")
        return restaurants_id_list

class RecommendWords(Recommend):
    '''
    口コミによるレコメンド
    ReviewRatingが3以上の店舗を返す
    一回のレスポンスで返す店舗数は0~10の間
    '''

    def pre_info(self, fetch_group, group_id, user_id):
        # YahooローカルサーチAPIで検索するクエリ
        pre_search_params = get_search_params_from_fetch_group(fetch_group)
        pre_search_params.update({
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
        })
        return pre_search_params
    
    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info):

        restaurants_info = sorted(pre_restaurants_info, key=lambda x:x['ReviewRating'], reverse=True)
        stop_index = [i for i, x in enumerate(restaurants_info) if x['ReviewRating'] < 3][0]
        restaurants_info = restaurants_info[:min(stop_index, RESULTS_COUNT)]
        return [r['Restaurant_id'] for r in restaurants_info]



# ============================================================================================================
# Yahoo Local Search テスト用

def local_search_test_URL(fetch_group, group_id, user_id):
    '''
    simpleのYahoo Local Searchの出力を見る
    '''
    coordinates = current_group[group_id]['Coordinates']
    request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    
     # YahooローカルサーチAPIで検索するクエリ
    search_params = {
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
    search_params.update(current_group[group_id]['FilterParams'])

    # Yahoo local search APIで店舗情報を取得
    local_search_url = 'https://map.yahooapis.jp/search/local/V1/localSearch'
    search_params.update({
        'appid': os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        'output': 'json',
        'detail': 'full'
    })
    return local_search_url + '?' + '&'.join([k+'='+str(v) for k,v in search_params.items()])



# ============================================================================================================
# recommend_mainで使う関数など
def normalize_pre_search_params(fetch_group, pre_search_params):
    if fetch_group.query is not None:
        pre_search_params['query'] = fetch_group.query + ' '
    if fetch_group.genre is not None:
        pre_search_params['query'] = fetch_group.genre
    if fetch_group.open_hour is not None:
        pre_search_params['open_day'] = str(fetch_group.open_day.day) + ',' + str(fetch_group.open_hour.hour)
    if fetch_group.max_price is not None:
        pre_search_params['maxprice'] = fetch_group.max_price
    if fetch_group.min_price is not None:
        pre_search_params['minprice'] = fetch_group.min_price
    return pre_search_params

def get_search_params_from_fetch_group(fetch_group, search_params={}):
    '''
    ユーザが指定した検索条件からAPIで使用する検索条件に変換
    '''
    search_params.update({
        'lat': fetch_group.lat, # 緯度
        'lon': fetch_group.lon, # 経度
        'dist': fetch_group.max_dist if fetch_group.max_dist is not None else MAX_DISTANCE, # 中心地点からの距離 # 最大20km
        'gc': '01', # グルメ
        'sort': fetch_group.sort if fetch_group.sort is not None else 'hyblid' # hyblid: 評価や距離などを総合してソート
    })

    if fetch_group.query is not None:
        search_params['query'] = fetch_group.query + ' '
    if fetch_group.genre is not None:
        search_params['query'] = fetch_group.genre
    if fetch_group.open_hour is not None:
        search_params['open'] = str(fetch_group.open_day.day) + ',' + str(fetch_group.open_hour.hour)
    if fetch_group.max_price is not None:
        search_params['maxprice'] = fetch_group.max_price
    if fetch_group.min_price is not None:
        search_params['minprice'] = fetch_group.min_price
    return search_params


def save_histories(group_id, user_id, restaurants_info):
    '''
    ユーザの表示履歴を保存する
    '''
    for i,r in enumerate(restaurants_info):
        fetch_history = session.query(History).filter(History.group==group_id, History.user==user_id, History.restaurant==r["Restaurant_id"]).first()
        if fetch_history is None:
            new_history = History()
            new_history.group = group_id
            new_history.user = user_id
            new_history.restaurant = r["Restaurant_id"]
            new_history.feeling = None
            session.add(new_history)
            session.commit()
        
        fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==r["Restaurant_id"]).first()
        if fetch_vote is None:
            new_vote = Vote()
            new_vote.group = group_id
            new_vote.restaurant = r["Restaurant_id"]
            new_vote.votes_all = 0
            new_vote.votes_like = 0
            session.add(new_vote)
            session.commit()
        else:
            if fetch_vote.votes_all==-1:
                fetch_vote.votes_all = 0
                fetch_vote.votes_like = 0
                session.commit()

# ============================================================================================================
# 未使用の関数？

def delete_duplicate_restaurants_info(group_id, user_id, restaurants_info):
    '''
    一度ユーザに送信したレストランはリストから除く

    Parameters
    ----------------
    group_id : int
    user_id : int
    restaurants_info : [dict]
    
    Returns
    ----------------
    restaurants_info : [dict]
        レストラン情報
    '''

    histories_restaurants = [h.restaurant for h in session.query(History.restaurant).filter(History.group==group_id, History.user==user_id).all()]
    return [ri for ri in restaurants_info if not ri['Restaurant_id'] in histories_restaurants]


def get_continued_restaurants(fetch_group, group_id, user_id):
    user_num = session.query(History).distinct(History.restaurant).filter(History.group==group_id, History.user==user_id).count()
    restaurant_num = session.query(Hisotry).distinct(History.restaurant).filter(History.group==group_id).count()
    restaurants_info = []
    return_restaurant_ids = []
    if user_num < restaurant_num:
        try:
            return_restaurant_ids = fetch_group[group_id]["RestaurantsOrder"][user_num:user_num+RESULTS_COUNT]
        except:
            return_restaurant_ids = fetch_group[group_id]["RestaurantsOrder"][user_num:]
    for i, r_id in enumerate(return_restaurant_ids):
        restaurants_info.append(fetch_group[group_id]['Restaurants'][r_id]['info'])
    return restaurants_info


def get_restaurants_info_price_filter(meanprice, restaurants_info):
    new_restaurants_info = []
    for restaurant_info in restaurants_info:
        if not restaurant_info['LunchPrice'] is None:
            if int(restaurant_info['LunchPrice']) > meanprice:
                continue

        if not restaurant_info['DinnerPrice'] is None:
            if int(restaurant_info['DinnerPrice']) > meanprice:
                continue

        new_restaurants_info.append(restaurant_info)

    return new_restaurants_info

# ============================================================================================================
# recommend.pyで最初に呼ばれる

def recommend_main(fetch_group, group_id, user_id):
    '''
    Yahoo local search APIで情報を検索し、json形式で情報を返す
    
    Parameters
    ----------------
    fetch_group : 
    group_id : int
    user_id : int
    
    Returns
    ----------------
    restaurants_info : [dict]
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
    recomm = RecommendSimple() # レコメンドに使うクラスを指定
    #recomm = RecommendTemplate() # レコメンドに使うクラスを指定
    #recomm = RecommendYahoo() # レコメンドに使うクラスを指定
    if recommend_method in ['rating', 'score', 'hyblid', 'review', 'kana', 'price', 'dist', 'geo', '-rating', '-score', '-hyblid', '-review', '-kana', '-price', '-dist', '-geo']:
        recomm = RecommendSimple()
    elif recommend_method == 'template':
        recomm = RecommendTemplate()
    elif recommend_method == 'review_words':
        recomm = RecommendWords()
    elif recommend_method == 'original':
        print("method=====================")
        print("original")
        recomm = RecommendOriginal()
        print("method=====================")
    elif recommend_method == 'local_search_test':
        return local_search_test(fetch_group, group_id, user_id)
    elif recommend_method == 'local_search_test_URL':
        return local_search_test_URL(fetch_group, group_id, user_id)

    # 結果が0件なら繰り返す
    for i in range(10):
        # 主な処理
            # 検索条件から、
        pre_search_params = recomm.pre_info(fetch_group, group_id, user_id)
            # APIで情報を取得し、
        pre_restaurants_info = api_functions.search_restaurants_info(fetch_group, group_id, user_id, pre_search_params, STOCK_COUNT)
            # ユーザに表示する店を選び、
        restaurants_ids = recomm.response_info(fetch_group, group_id, user_id, pre_restaurants_info)
            # 店舗情報を返す。
        restaurants_info = api_functions.get_restaurants_info(fetch_group, group_id, restaurants_ids)

        print(f"RecommendMethod:{recommend_method}")
        print(f"data_num {len(restaurants_info)}")
        if len(restaurants_info) >= 1:
            # 履歴を保存
            save_histories(group_id, user_id, restaurants_info)
            return restaurants_info
    
    # originalでダメならば、simpleで返す　TODO
    if recommend_method=="original":
        if len(restaurants_info) == 0:
            recomm = RecommendSimple()
            recommend_method = "simple"
            for i in range(10):
                # 主な処理
                    # 検索条件から、
                pre_search_params = recomm.pre_info(fetch_group, group_id, user_id)
                    # APIで情報を取得し、
                pre_restaurants_info = api_functions.search_restaurants_info(fetch_group, group_id, user_id, pre_search_params, STOCK_COUNT)
                    # ユーザに表示する店を選び、
                restaurants_ids = recomm.response_info(fetch_group, group_id, user_id, pre_restaurants_info)
                    # 店舗情報を返す。
                restaurants_info = api_functions.get_restaurants_info(fetch_group, group_id, restaurants_ids)

                print(f"RecommendMethod:{recommend_method}")
                print(f"data_num {len(restaurants_info)}")
                if len(restaurants_info) >= 1:
                    # 履歴を保存
                    save_histories(group_id, user_id, restaurants_info)
                    return restaurants_info
