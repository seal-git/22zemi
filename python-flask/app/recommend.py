from app import api_functions, calc_info
import json
import os
import random
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from sqlalchemy import distinct
from abc import ABCMeta, abstractmethod
import math
import sys
import numpy as np
import sklearn
from sklearn.svm import SVR
# import threading


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
    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
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

        histories_restaurants : [string]
            既にユーザに送信した店のリスト


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
            'stock': STOCK_COUNT
        })
        return pre_search_params

    
    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
        # 一度ユーザに送信したレストランはリストから除く
        pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)

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
        # pre_search_params.update({
        #     'image': 'true', # 画像がある店
        #     'open': 'now', # 現在開店している店舗
        #     'stock': RESULTS_COUNT,
        #     #'start': RESULTS_COUNT * (session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()).request_count, # 表示範囲：開始位置
        #     #'results': RESULTS_COUNT, # 表示範囲：店舗数
        # })
        return pre_search_params


    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
        # 一度ユーザに送信したレストランはリストから除く
        restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)

        # if fetch_group.max_price is not None: restaurants_info = get_restaurants_info_price_filter(fetch_group.max_price, restaurants_info)
        restaurants_info = restaurants_info[:RESULTS_COUNT] # 指定した数だのお店だけを選択
        return [r['Restaurant_id'] for r in restaurants_info]


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
            'stock': RESULTS_COUNT,
            #'start': RESULTS_COUNT * (session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()).request_count, # 表示範囲：開始位置
            #'results': RESULTS_COUNT, # 表示範囲：店舗数
        })
        return pre_search_params

    
    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
        # 一度ユーザに送信したレストランはリストから除く
        pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)

        # 何もしない
        return [r['Restaurant_id'] for r in pre_restaurants_info]


class RecommendOriginal(Recommend):
    def pre_info(self, fetch_group):
        # YahooローカルサーチAPIで検索するクエリ
        pre_search_params = get_search_params_from_fetch_group(fetch_group)
        pre_search_params.update({
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'stock': STOCK_COUNT,
        })
        return pre_search_params

    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
        # 一度ユーザに送信したレストランはリストから除く
        pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)

        voted= [[v.restaurant, v.votes_like, v.votes_all] for v in session.query(Vote).filter(Vote.group==group_id, Vote.votes_all>0).all()]
        if len(voted) == 0:
            return [r['Restaurant_id'] for r in pre_restaurants_info][0:RESULTS_COUNT]
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
                price_average = weight_price / keep_count
                distance_average = weight_distance / keep_count
                fetch_group.price_average = price_average
                fetch_group.distance_average = distance_average
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
                if r["Price"] <= price_average * 2:
                        if r["distance_float"] <= distance_average * 1.5:
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
            print(price_average)
            print(distance_average)
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
            'stock': STOCK_COUNT,
        })
        return pre_search_params
    
    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
        # 一度ユーザに送信したレストランはリストから除く
        pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)

        restaurants_info = sorted(pre_restaurants_info, key=lambda x:x['ReviewRating'], reverse=True)
        stop_index = [i for i, x in enumerate(restaurants_info) if x['ReviewRating'] < 3][0]
        restaurants_info = restaurants_info[:min(stop_index, RESULTS_COUNT)]
        return [r['Restaurant_id'] for r in restaurants_info]



class RecommendQueue(Recommend):
    '''
    キューを持っておいてレコメンドする
    '''


    def __calc_recommend_priority(self, fetch_group, group_id, pre_restaurants_info):
        '''
        Vote.recommend_priorityを計算する。
        '''
        # 価格と距離の平均と標準偏差を求める --------
        like_price_count = 0
        like_price_sum = 0
        like_price2_sum = 0
        like_distance_count = 0
        like_distance_sum = 0
        like_distance2_sum = 0
        genre_list = []
        like_genre_count = []

        dislike_price_count = 0
        dislike_price_sum = 0
        dislike_price2_sum = 0
        dislike_distance_count = 0
        dislike_distance_sum = 0
        dislike_distance2_sum = 0
        dislike_genre_count = []

        for r in pre_restaurants_info:
            vote_like = r["VotesLike"]
            vote_dislike = r["VotesAll"] - vote_like
            if r["VotesAll"] <= 0:
                continue

            #price処理
            price = r["Price"]
            if price is not None and price != 0:
                like_price_sum += vote_like * price
                like_price2_sum += vote_like * price*price
                like_price_count += vote_like
                dislike_price_sum += vote_dislike * price
                dislike_price2_sum += vote_dislike * price*price
                dislike_price_count += vote_dislike

            #distance処理
            distance = r["distance_float"]
            like_distance_sum += vote_like * distance
            like_distance2_sum += vote_like * distance*distance
            like_distance_count += vote_like
            dislike_distance_sum += vote_dislike * distance
            dislike_distance2_sum += vote_dislike * distance*distance
            dislike_distance_count += vote_dislike

            #genre処理
            genre = r["Genre"]
            for g in genre:
                if g["Name"] not in genre_list:
                    genre_list.append(g["Name"])
                    like_genre_count.append(vote_like)
                    dislike_genre_count.append(vote_dislike)
                else:
                    like_genre_count[genre_list.index(g["Name"])] += vote_like
                    dislike_genre_count[genre_list.index(g["Name"])] += vote_dislike

        genre_feeling = {genre: {'Like':like,'Dislike':dislike} for genre, like, dislike in zip(genre_list, like_genre_count, dislike_genre_count)}
        like_price_average = like_price_sum / like_price_count if like_price_count != 0 else 0
        like_distance_average = like_distance_sum / like_distance_count if like_distance_count != 0 else 0
        like_price_sigma = math.sqrt(like_price2_sum / like_price_count) if like_price_count != 0 else sys.float_info.max/16
        like_distance_sigma = math.sqrt(like_distance2_sum / like_distance_count) if like_distance_count != 0 else sys.float_info.max/16
        dislike_price_average = dislike_price_sum / dislike_price_count if dislike_price_count != 0 else 0
        dislike_distance_average = dislike_distance_sum / dislike_distance_count if dislike_distance_count != 0 else 0
        dislike_price_sigma = math.sqrt(dislike_price2_sum / dislike_price_count) if dislike_price_count != 0 else sys.float_info.max/16
        dislike_distance_sigma = math.sqrt(dislike_distance2_sum / dislike_distance_count) if dislike_distance_count != 0 else sys.float_info.max/16
        fetch_group.price_average = like_price_average
        fetch_group.distance_average = like_distance_average
        session.commit()

        # recommend_priorityを計算する。 --------
        weight_votes_like = 2.5
        weight_price = 0.4
        weight_distance = 0.3
        weight_genre = 0.3
        alln = session.query(Belong).filter(Belong.group==group_id).count() # 参加人数
        for ri in pre_restaurants_info:
            fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==ri['Restaurant_id']).one()
            
            # votes_like_score
            votes_like_score = alln * (fetch_vote.votes_all - fetch_vote.votes_like) - fetch_vote.votes_like # 1人でも反対した店は後回し
            
            # price_score
            price = ri['Price']
            if price is not None and price != 0:
                price_score = (abs(price - like_price_average) / like_price_sigma - abs(price - dislike_price_average) / dislike_price_sigma) / 1000 # 偏差値のような何か
            else:
                price_score = 1024 # 価格表示の無いものは後回しにしたいので，大きいスコアを与える
            
            # distance_score
            distance = ri['distance_float']
            distance_score = abs(distance - like_distance_average) / like_distance_sigma - abs(distance - dislike_distance_average) / dislike_distance_sigma # 偏差値のような何か
            
            # genre_score
            genre_score = 0
            for g in [gt['Name'] for gt in ri['Genre']]:
                if g in genre_feeling:
                    genre_score += genre_feeling[g]['Dislike'] - genre_feeling[g]['Like']
            
            fetch_vote.recommend_priority = votes_like_score * weight_votes_like + price_score * weight_price + distance_score * weight_distance + genre_score * weight_genre
            session.commit()


    def pre_info(self, fetch_group, group_id, user_id):
        # YahooローカルサーチAPIで検索するクエリ
        pre_search_params = get_search_params_from_fetch_group(fetch_group)
        pre_search_params.update({
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'stock': STOCK_COUNT,
        })
        return pre_search_params
 

    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):

        fetch_votes = session.query(Vote.votes_all).filter(Vote.group==group_id, Vote.votes_all>0).all()
        if sum([v.votes_all for v in fetch_votes]) < 3:
            pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)
            return [r['Restaurant_id'] for r in pre_restaurants_info][0:RESULTS_COUNT]
        
        # Vote.recommend_priorityを計算する。
        self.__calc_recommend_priority(fetch_group, group_id, pre_restaurants_info)
        # t = threading.Thread(target=self.__calc_recommend_priority, args=(fetch_group, group_id, pre_restaurants_info))
        # t.start()

        # recommend_priorityの小さい順にユーザに送信する。
        fetch_votes = session.query(Vote).filter(Vote.group==group_id, Vote.recommend_priority is not None).order_by(Vote.recommend_priority).all()
        restaurants_ids = []
        for fv in fetch_votes:
            if fv.restaurant not in histories_restaurants:
                restaurants_ids.append(fv.restaurant)
                if len(restaurants_ids) == RESULTS_COUNT:
                    return restaurants_ids
        return restaurants_ids


class RecommendSVM(Recommend):
    '''
    RecommendQueueの重みをSVMで決める

    1. 投票された結果はLIKE数の多い順に表示
    2. 未投票の結果は価格・距離・ジャンルからSVMで評価値を推定して表示
    '''


    def __calc_recommend_priority(self, fetch_group, group_id, pre_restaurants_info):
        '''
        Vote.recommend_priorityを計算する。
        投票数が0だと死ぬ
        '''
        # 価格と距離の平均と標準偏差を求める --------
        like_price_count = 0
        like_price_sum = 0
        like_price2_sum = 0
        like_distance_count = 0
        like_distance_sum = 0
        like_distance2_sum = 0
        genre_list = []
        like_genre_count = []

        dislike_price_count = 0
        dislike_price_sum = 0
        dislike_price2_sum = 0
        dislike_distance_count = 0
        dislike_distance_sum = 0
        dislike_distance2_sum = 0
        dislike_genre_count = []

        voted_restaurants_count = 0

        for r in pre_restaurants_info:
            if r["VotesAll"] <= 0:
                continue
            voted_restaurants_count += 1
            vote_like = r["VotesLike"]
            vote_dislike = r["VotesAll"] - vote_like
            

            #price処理
            price = r["Price"]
            if price is not None and price != 0:
                like_price_sum += vote_like * price
                like_price2_sum += vote_like * price*price
                like_price_count += vote_like
                dislike_price_sum += vote_dislike * price
                dislike_price2_sum += vote_dislike * price*price
                dislike_price_count += vote_dislike

            #distance処理
            distance = r["distance_float"]
            like_distance_sum += vote_like * distance
            like_distance2_sum += vote_like * distance*distance
            like_distance_count += vote_like
            dislike_distance_sum += vote_dislike * distance
            dislike_distance2_sum += vote_dislike * distance*distance
            dislike_distance_count += vote_dislike

            #genre処理
            genre = r["Genre"]
            for g in genre:
                if g["Name"] not in genre_list:
                    genre_list.append(g["Name"])
                    like_genre_count.append(vote_like)
                    dislike_genre_count.append(vote_dislike)
                else:
                    like_genre_count[genre_list.index(g["Name"])] += vote_like
                    dislike_genre_count[genre_list.index(g["Name"])] += vote_dislike

        genre_feeling = {genre: {'Like':like,'Dislike':dislike} for genre, like, dislike in zip(genre_list, like_genre_count, dislike_genre_count)}
        like_price_average = like_price_sum / like_price_count if like_price_count != 0 else 0
        like_distance_average = like_distance_sum / like_distance_count if like_distance_count != 0 else 0
        like_price_sigma = math.sqrt(like_price2_sum / like_price_count) if like_price_count != 0 else sys.float_info.max/16
        like_distance_sigma = math.sqrt(like_distance2_sum / like_distance_count) if like_distance_count != 0 else sys.float_info.max/16
        dislike_price_average = dislike_price_sum / dislike_price_count if dislike_price_count != 0 else 0
        dislike_distance_average = dislike_distance_sum / dislike_distance_count if dislike_distance_count != 0 else 0
        dislike_price_sigma = math.sqrt(dislike_price2_sum / dislike_price_count) if dislike_price_count != 0 else sys.float_info.max/16
        dislike_distance_sigma = math.sqrt(dislike_distance2_sum / dislike_distance_count) if dislike_distance_count != 0 else sys.float_info.max/16
        fetch_group.price_average = like_price_average
        fetch_group.distance_average = like_distance_average
        session.commit()

        # recommend_priorityを計算する。--------

        alln = session.query(Belong).filter(Belong.group==group_id).count() # 参加人数
        unvoted_restaurants_count = len(pre_restaurants_info) - voted_restaurants_count

        # 学習のためのベクトル生成
        VEC_SIZE = 7
        rid_train = [''] * voted_restaurants_count
        x_train = np.zeros((voted_restaurants_count, VEC_SIZE))
        y_train = np.zeros(voted_restaurants_count)
        i_train = 0
        rid_test = [''] * unvoted_restaurants_count
        x_test = np.zeros((unvoted_restaurants_count, VEC_SIZE))
        y_test = np.zeros(unvoted_restaurants_count)
        i_test = 0

        for r in pre_restaurants_info:

            vec = np.zeros(VEC_SIZE)

            # price_score
            price = r['Price']
            if price is not None and price != 0:
                vec[0] = abs(price - like_price_average) / like_price_sigma
                vec[1] = -abs(price - dislike_price_average) / dislike_price_sigma
                vec[2] = price / 1000
            else:
                vec[0] = 0
                vec[1] = 0
                if (like_price_count + dislike_price_count) == 0:
                    vec[2] = (like_price_average + dislike_price_average) / 2
                else:
                    vec[2] = (like_price_average * like_price_count + dislike_price_average * dislike_price_count) / (like_price_count + dislike_price_count)

            # distance_score
            distance = r['distance_float']
            vec[3] = abs(distance - like_distance_average) / like_distance_sigma * 1000
            vec[4] = -abs(distance - dislike_distance_average) / dislike_distance_sigma * 1000
            
            # genre_score
            genre_score = 0
            for g in [gt['Name'] for gt in r['Genre']]:
                if g in genre_feeling:
                    genre_score += genre_feeling[g]['Dislike'] - genre_feeling[g]['Like']
            vec[5] = genre_score * 1000

            vec[6] = r['ReviewRatingFloat']

            # 変数に格納
            if r["VotesAll"] <= 0:
                rid_test[i_test] = r["Restaurant_id"]
                x_test[i_test][:] = vec[:]
                i_test += 1
            else:
                rid_train[i_train] = r["Restaurant_id"]
                x_train[i_train][:] = vec[:]
                y_train[i_train] = alln * (r["VotesAll"] - r["VotesLike"]) - r["VotesLike"] # 訓練データのラベル
                i_train += 1


        print("itest=", i_test, " , unvoted_restaurants_count=", unvoted_restaurants_count)
        if i_test <= 0:
            for rid, y in zip(rid_train, y_train):
                fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==rid).one()
                fetch_vote.recommend_priority = y
                session.commit()
            return

        # 学習器で評価値を求める
        # regressor = sklearn.linear_model.LogisticRegression() # ロジスティック回帰
        regressor = SVR() # SVM
        regressor.fit(x_train, y_train)
        y_train = regressor.predict(x_train)
        y_test = regressor.predict(x_test)
        
        for rid, y in zip(rid_train, y_train):
            fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==rid).one()
            fetch_vote.recommend_priority = y
            session.commit()
        for rid, y in zip(rid_test, y_test):
            fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==rid).one()
            fetch_vote.recommend_priority = y
            session.commit()


    def pre_info(self, fetch_group, group_id, user_id):
        # YahooローカルサーチAPIで検索するクエリ
        pre_search_params = get_search_params_from_fetch_group(fetch_group)
        pre_search_params.update({
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'stock': STOCK_COUNT,
        })
        return pre_search_params
 

    def response_info(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):

        fetch_votes = session.query(Vote.votes_all).filter(Vote.group==group_id, Vote.votes_all>0).all()
        if sum([v.votes_all for v in fetch_votes]) < 3:
            pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)
            return [r['Restaurant_id'] for r in pre_restaurants_info][0:RESULTS_COUNT]
        
        # Vote.recommend_priorityを計算する。
        self.__calc_recommend_priority(fetch_group, group_id, pre_restaurants_info)
        # t = threading.Thread(target=self.__calc_recommend_priority, args=(fetch_group, group_id, pre_restaurants_info))
        # t.start()

        # recommend_priorityの小さい順にユーザに送信する。
        fetch_votes = session.query(Vote).filter(Vote.group==group_id, Vote.recommend_priority is not None).order_by(Vote.recommend_priority).all()
        restaurants_ids = []
        for fv in fetch_votes:
            if fv.restaurant not in histories_restaurants:
                restaurants_ids.append(fv.restaurant)
                if len(restaurants_ids) == RESULTS_COUNT:
                    return restaurants_ids
        return restaurants_ids




# ============================================================================================================
# Yahoo Local Search テスト用

# def local_search_test_URL(fetch_group, group_id, user_id):
#     '''
#     simpleのYahoo Local Searchの出力を見る
#     '''
#     coordinates = current_group[group_id]['Coordinates']
#     request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    
#      # YahooローカルサーチAPIで検索するクエリ
#     search_params = {
#         # 中心地から1km以内のグルメを検索
#         'lat': coordinates[0], # 緯度
#         'lon': coordinates[1], # 経度
#         'dist': MAX_DISTANCE, # 中心地点からの距離 # 最大20km
#         'gc': '01', # グルメ
#         'image': True, # 画像がある店
#         'open': 'now', # 現在開店している店舗
#         'sort': 'hybrid', # 評価や距離などを総合してソート
#         'start': RESULTS_COUNT * request_count, # 表示範囲：開始位置
#         'results': RESULTS_COUNT # 表示範囲：店舗数
#     }
#     search_params.update(current_group[group_id]['FilterParams'])

#     # Yahoo local search APIで店舗情報を取得
#     local_search_url = 'https://map.yahooapis.jp/search/local/V1/localSearch'
#     search_params.update({
#         'appid': os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
#         'output': 'json',
#         'detail': 'full'
#     })
#     return local_search_url + '?' + '&'.join([k+'='+str(v) for k,v in search_params.items()])



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
    api_method = fetch_group.api_method
    if api_method == "yahoo":
        search_params.update({
            'lat': fetch_group.lat, # 緯度
            'lon': fetch_group.lon, # 経度
            'dist': fetch_group.max_dist if fetch_group.max_dist is not None else MAX_DISTANCE, # 中心地点からの距離 # 最大20km
            'gc': '01', # グルメ
            'sort': fetch_group.sort if fetch_group.sort is not None else 'hyblid' # hyblid: 評価や距離などを総合してソート
        })
    elif api_method == "google":
        search_params.update({
            'location': f'{fetch_group.lat},{fetch_group.lon}', # 緯度,経度
            'radius': fetch_group.max_dist * 1000 if fetch_group.max_dist is not None else MAX_DISTANCE * 1000, # 半径 m
            'type': 'restaurant',
        })

    # if fetch_group.query is not None:
    #     search_params['query'] = fetch_group.query + ' '
    # if fetch_group.genre is not None:
    #     search_params['query'] = fetch_group.genre
    # if fetch_group.open_hour is not None:
    #     search_params['open'] = str(fetch_group.open_day.day) + ',' + str(fetch_group.open_hour.hour)
    # if fetch_group.max_price is not None:
    #     search_params['maxprice'] = fetch_group.max_price
    # if fetch_group.min_price is not None:
    #     search_params['minprice'] = fetch_group.min_price
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


def delete_duplicate_restaurants_info(group_id, user_id, restaurants_info, histories_restaurants=None):
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
    if histories_restaurants is None:
        histories_restaurants = [h.restaurant for h in session.query(History.restaurant).filter(History.group==group_id, History.user==user_id).all()]
    return [ri for ri in restaurants_info if not ri['Restaurant_id'] in histories_restaurants]

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
    #recomm = RecommendSimple()
    #recomm = RecommendTemplate()
    #recomm = RecommendYahoo()
    #recomm = RecommendQueue()
    recomm = RecommendSVM()
    if recommend_method in ['rating', 'score', 'hyblid', 'review', 'kana', 'price', 'dist', 'geo', '-rating', '-score', '-hyblid', '-review', '-kana', '-price', '-dist', '-geo']:
        recomm = RecommendSimple()
    elif recommend_method == 'template':
        recomm = RecommendTemplate()
    elif recommend_method == 'review_words':
        recomm = RecommendWords()
    elif recommend_method == 'original':
        recomm = RecommendOriginal()
    # elif recommend_method == 'local_search_test':
    #     return local_search_test(fetch_group, group_id, user_id)
    # elif recommend_method == 'local_search_test_URL':
    #     return local_search_test_URL(fetch_group, group_id, user_id)


    # 重複して表示しないようにするため、履歴を取得
    histories_restaurants = [h.restaurant for h in session.query(History.restaurant).filter(History.group==group_id, History.user==user_id).all()]
    
    # 結果が0件なら繰り返す
    for i in range(3):
        # 主な処理
            # 検索条件から、
        pre_search_params = recomm.pre_info(fetch_group, group_id, user_id)
        print("=========================")
        print("pre_search_params")
        print(pre_search_params)
        print("=========================")
            # APIで情報を取得し、
        pre_restaurants_info = api_functions.search_restaurants_info(fetch_group, group_id, user_id, pre_search_params, histories_restaurants)
        print("stock =", len(pre_restaurants_info), ", history =", len(histories_restaurants))
            # ユーザに表示する店を選び、
        restaurants_ids = recomm.response_info(fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants)
            # 店舗情報を返す。
        restaurants_info = api_functions.get_restaurants_info(fetch_group, group_id, restaurants_ids)

        print(f"data_num {len(restaurants_info)}")
        if len(restaurants_info) >= 1:
            # 履歴を保存
            save_histories(group_id, user_id, restaurants_info)
            return restaurants_info
        else:
            if i > 1:
                histories_restaurants = [] # 結果が0件のときは履歴をなかったことにしてもう一周
    
    # originalでダメならば、simpleで返す　TODO
    if recommend_method=="original":
        if len(restaurants_info) == 0:
            recomm = RecommendSimple()
            recommend_method = "simple"
            for i in range(10):
                    # 検索条件から、
                pre_search_params = recomm.pre_info(fetch_group, group_id, user_id)
                        # 重複して表示しないようにするため、履歴を取得
                histories_restaurants = [h.restaurant for h in session.query(History.restaurant).filter(History.group==group_id, History.user==user_id).all()]
                    # APIで情報を取得し、
                pre_restaurants_info = api_functions.search_restaurants_info(fetch_group, group_id, user_id, pre_search_params, histories_restaurants)
                    # ユーザに表示する店を選び、
                restaurants_ids = recomm.response_info(fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants)
                    # 店舗情報を返す。
                restaurants_info = api_functions.get_restaurants_info(fetch_group, group_id, restaurants_ids)

                print(f"RecommendMethod:{recommend_method}")
                print(f"data_num {len(restaurants_info)}")
                if len(restaurants_info) >= 1:
                    # 履歴を保存
                    save_histories(group_id, user_id, restaurants_info)
                    return restaurants_info
    return []
