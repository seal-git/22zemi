import json
import os
import random
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from app.internal_info import *
from app import database_functions, api_functions, calc_info, config, call_api
from sqlalchemy import distinct
from abc import ABCMeta, abstractmethod
import math
import sys
import numpy as np
import sklearn
from sklearn.svm import SVR
import threading


'''

レコメンドを行う。
================
recommend_main関数が最初に呼ばれる。

# 主な流れ
1. search関数で候補となる店の情報を取得する。ユーザが指定した検索条件はこの段階で絞りたい。
2. filter関数でユーザに表示する店を選ぶ。レコメンドアルゴリズムはここに記述したい。

# 新しいレコメンドの記述
 - Recommendクラスを継承して、レコメンドアルゴリズムを記述してください。
 - RecommendTemplateクラスの例を参考にしてください。
 - recommend_mainに作ったクラスを追加してください。

'''

RESPONSE_COUNT = config.MyConfig.RESPONSE_COUNT # 一回に返す店舗の数
STOCK_COUNT = config.MyConfig.STOCK_COUNT # APIで取得するデータの数
MAX_DISTANCE = config.MyConfig.MAX_DISTANCE # 中心地からの距離 上限20000m

#カテゴリの類似度が高い物
with open("./data/category_high_sim.json","rb") as f:
    category_high_sim = json.load(f)
#カテゴリの類似度が低い物
with open("./data/category_low_sim.json","rb") as f:
    category_low_sim = json.load(f)
class Recommend(metaclass=ABCMeta):

    @abstractmethod
    def set_search_params(self, fetch_group, group_id, user_id, params, histories_restaurants):
        '''
        検索条件を設定する

        Parameters
        ----------------
        fetch_group : Group
            データベースのGroupテーブルの情報

        group_id : int

        user_id : int

        Returns
        ----------------
        pre_search_params : Param

        '''
        pass

    @abstractmethod
    def calc_priority(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
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


class RecommendSimple(Recommend):
    def calc_priority(self,
                   fetch_group,
                   group_id,
                   user_id,
                   restaurants_info,
                   histories_restaurants):
        restaurants_info = filter_by_price(fetch_group.max_price,
                                               fetch_group.min_price,
                                               restaurants_info)

        for i, _ in enumerate(restaurants_info):
            restaurants_info[i].recommend_priority += 1

        return restaurants_info

    def set_search_params(self,
                          fetch_group,
                          group_id,
                          user_id,
                          params,
                          histories_restaurants):
        # YahooローカルサーチAPIで検索するクエリ

        # 検索条件を追加
        params.sort = "hybrid"

        return params
#カテゴリの業種コード3, 検索用


# ============================================================================================================
# Recommendクラス関連

with open("./data/category_code.json","rb") as f:
    category_code = json.load(f)


class RecommendTemplate(Recommend):
    '''
    例
    '''
    def set_search_params(self,
                          fetch_group,
                          group_id,
                          user_id,
                          params,
                          histories_restaurants
                          ):
        # YahooローカルサーチAPIで検索する
        # グループの検索条件を取得
        search_params = database_functions.get_search_params_from_fetch_group(fetch_group)

        # 検索条件を追加
        search_params.image = True # 画像がある店
        search_params.open_now = True # 現在開店している店舗
        search_params.set_start_and_results_from_stock(group_id, STOCK_COUNT, histories_restaurants)

        return search_params

    def calc_priority(self,
               fetch_group,
               group_id,
               user_id,
               pre_restaurants_info,
               histories_restaurants
               ):
        # 一度ユーザに送信したレストランはリストから除く
        pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)
        pre_restaurants_info = filter_by_price(fetch_group.max_price, fetch_group.min_price, pre_restaurants_info)

        # TODO: 重みを計算
        weight = [0] * len(pre_restaurants_info)
        for i, pre_restaurant_info in enumerate(pre_restaurants_info):
            weight[i] = len(pre_restaurants_info) - i

        # 重み順にソートして出力
        restaurants_info_tuple = sorted(zip(weight, pre_restaurants_info), key=lambda x:x[0], reverse=True)
        restaurants_ids = [rj[1].id for rj in restaurants_info_tuple]
        return restaurants_ids[0: RESPONSE_COUNT]


# class RecommendYahoo(Recommend):
#     '''
#     レコメンドは Yahoo Local Search に任せる
#     '''

#     def search(self, fetch_group, group_id, user_id, histories_restaurants):
#         """
#         YahooローカルサーチAPIで検索する
#         Returns
#         -------
#         restaurants_info: RestaurantsInfo
#         """
#         search_params = database_functions.get_search_params_from_fetch_group(fetch_group)

#         # 検索条件を追加
#         search_params.image = True  # 画像がある店
#         search_params.open_now = True  # 現在開店している店舗
#         search_params.sort = "hybrid"  # 評価や距離などを総合してソート
#         ## start, resultsを指定
#         request_count = (session.query(Belong).filter(Belong.group==group_id,
#                                                       Belong.user==user_id).one()
#                          ).request_count
#         search_params.start = config.MyConfig.RESPONSE_COUNT * request_count
#         search_params.results = config.MyConfig.RESPONSE_COUNT

#         # Yahoo_local_searchで検索
#         return call_api.search_restaurants_info(fetch_group,
#                                                 group_id,
#                                                 user_id,
#                                                 search_params)

    
#     def calc_priority(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
#         # 一度ユーザに送信したレストランはリストから除く
#         pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)

#         # 指定した数のお店だけを選択
#         restaurants_info = pre_restaurants_info[:RESPONSE_COUNT]
#         return restaurants_info


# class RecommendOriginal(Recommend):
#     def search(self, fetch_group, group_id, user_id, histories_restaurants):
#         # YahooローカルサーチAPIで検索するクエリ
#         search_params = database_functions.get_search_params_from_fetch_group(fetch_group)

#         # 検索条件を追加
#         search_params.image = True  # 画像がある店
#         search_params.open_now = True  # 現在開店している店舗
#         search_params.set_start_and_results_from_stock(group_id, STOCK_COUNT, histories_restaurants)

#         # Yahooの形式にして検索
#         return call_api.search_restaurants_info(fetch_group, group_id,
#                                                      user_id, search_params)

#     def calc_priority(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
#         # 一度ユーザに送信したレストランはリストから除く
#         pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)
#         pre_restaurants_info = restaurants_info_price_filter(fetch_group.max_price, fetch_group.min_price, pre_restaurants_info)

#         voted= [[v.restaurant, v.votes_like, v.votes_all] for v in session.query(Vote).filter(Vote.group==group_id, Vote.votes_all>0).all()]
#         if len(voted) == 0:
#             return [r.id for r in pre_restaurants_info][0:RESPONSE_COUNT]
#         else:
#             #keepに関して
#             keep_restaurant_ids = [v[0] for v in voted if v[1] > 0]
#             if len(keep_restaurant_ids) > 0:
#                 keep_count = 0
#                 keep_genre = [] #keepした店のgenre
#                 keep_genre_count = []
#                 weight_price = 0
#                 weight_distance = 0
#                 keep_restaurants_info = database_functions.load_restaurants_info(keep_restaurant_ids)
#                 keep_restaurants_info = calc_info.add_votes_distance(fetch_group, group_id, keep_restaurants_info)
#                 for r in keep_restaurants_info:
#                     id = r["Restaurant_id"]
#                     votelike = r.votes_like
#                     #price処理
#                     price = r.price
#                     try:
#                         weight_price += votelike * price
#                     except:
#                         pass
#                     #distance処理
#                     distance = r["distance_float"]
#                     weight_distance += votelike * distance
#                     #genre処理
#                     genre = r["Genre"]
#                     for g in genre:
#                         if g["Name"] not in keep_genre:
#                             keep_genre.append(g["Name"])
#                             keep_genre_count.append(votelike)
#                         else:
#                             keep_genre_count[keep_genre.index(g["Name"])] += votelike
#                     #keep数
#                     keep_count += votelike

#                 keep_genre_rank = [[count, genre] for count, genre in zip(keep_genre_count, keep_genre)]
#                 keep_genre_rank.sort(reverse=True)
#                 price_average = weight_price / keep_count
#                 distance_average = weight_distance / keep_count
#                 fetch_group.price_average = price_average
#                 fetch_group.distance_average = distance_average
#                 session.commit()

#             #throughに関して
#             through_restaurant_ids = [v[0] for v in voted if v[1] == 0]
#             if len(through_restaurant_ids) > 0:
#                 through_genre = [] #throughした店のgenre
#                 through_genre_count = []
#                 through_restaurants_info = database_functions.load_restaurants_info(through_restaurant_ids)
#                 through_restaurants_info = calc_info.add_votes_distance(fetch_group, group_id, through_restaurants_info)
#                 for r in through_restaurants_info:
#                     id = r["Restaurant_id"]
#                     # votelike = r.votes_like
#                     # voteall = r.votes_all
#                     # votedislike = voteall - votelike
#                     #genre処理
#                     genre = r["Genre"]
#                     for g in genre:
#                         if g["Name"] not in through_genre:
#                             through_genre.append(g["Name"])
#                             #through_genre_count.append(votedislike)
#                         # else:
#                         #     through_genre_count[keep_genre.index(g["Name"])] += votedislike
#                 #through_genre_rank = [[count, genre] for count, genre in zip(through_genre_count, through_genre)]
#                 #through_genre_rank.sort(reverse=True)

#             try:
#                 if len(keep_restaurant_ids) == len(voted):#全部keepなら
#                     high_rank_genre = [g[1] for g in keep_genre_rank if g[0]==max(keep_genre_count)]
#                     recommend_genre = random.choice(category_high_sim[random.choice(high_rank_genre)])
#                     recommend_type = "high_sim"
#                 else:
#                     if random.random() < 0.7:
#                         if len(keep_genre) > 0:
#                             high_rank_genre = [g[1] for g in keep_genre_rank if g[0]==max(keep_genre_count)]
#                             recommend_genre = random.choice(category_high_sim[random.choice(high_rank_genre)])
#                             recommend_type = "high_sim"
#                         else:#全部throughなら
#                             recommend_genre = random.choice(category_low_sim[random.choice(through_genre)])
#                             recommend_type = "low_sim"
#                     else:
#                         recommend_genre = random.choice(category_low_sim[random.choice(through_genre)])
#                         recommend_type = "low_sim"
#             except:
#                 recommend_type = "non genre"
#                 recommend_genre = ""
            
#             # 履歴からrecommendするお店を取得
#             non_voted_restaurant_ids =[v.restaurant for v in session.query(Vote).filter(Vote.votes_all==-1)]
#             recommend_restaurants_info = database_functions.load_restaurants_info(non_voted_restaurant_ids)
#             recommend_restaurants_info = calc_info.add_votes_distance(fetch_group, group_id, recommend_restaurants_info)
#             restaurants_id_list = []
#             for r in recommend_restaurants_info:
#                 if r.price <= price_average * 2:
#                         if r["distance_float"] <= distance_average * 1.5:
#                             if recommend_genre != "":#genreがあれば
#                                 genre = r["Genre"]
#                                 for g in genre:
#                                     if g["Name"] == recommend_genre:
#                                         restaurants_id_list.append(r["Restaurant_id"])
#                             else:
#                                 restaurants_id_list.append(r["Restaurant_id"])
#             print("===================================")
#             print(recommend_type)
#             print(recommend_genre)
#             print(price_average)
#             print(distance_average)
#             print(restaurants_id_list)
#             print("===================================")
#         return restaurants_id_list

# class RecommendWords(Recommend):
#     '''
#     口コミによるレコメンド
#     ReviewRatingが3以上の店舗を返す
#     一回のレスポンスで返す店舗数は0~10の間
#     '''
#     def search(self, fetch_group, group_id, user_id, histories_restaurants):
#         # YahooローカルサーチAPIで検索するクエリ
#         search_params = database_functions.get_search_params_from_fetch_group(fetch_group)

#         # 検索条件を追加
#         search_params.image = True  # 画像がある店
#         search_params.open_now = True  # 現在開店している店舗
#         search_params.set_start_and_results_from_stock(group_id, STOCK_COUNT, histories_restaurants)

#         # Yahooで検索
#         return call_api.search_restaurants_info(fetch_group, group_id,
#                                                      user_id, search_params)

#     def calc_priority(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):
#         # 一度ユーザに送信したレストランはリストから除く
#         pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)
#         pre_restaurants_info = restaurants_info_price_filter(fetch_group.max_price, fetch_group.min_price, pre_restaurants_info)

#         restaurants_info = sorted(pre_restaurants_info, key=lambda x:x['ReviewRating'], reverse=True)
#         stop_index = [i for i, x in enumerate(restaurants_info) if x['ReviewRating'] < 3][0]
#         restaurants_info = restaurants_info[:min(stop_index, RESPONSE_COUNT)]
#         return [r.id for r in restaurants_info]



# class RecommendQueue(Recommend):
#     '''
#     キューを持っておいてレコメンドする
#     '''


#     def __calc_recommend_priority(self, fetch_group, group_id, pre_restaurants_info):
#         '''
#         Vote.recommend_priorityを計算する。
#         '''
#         # 価格と距離の平均と標準偏差を求める --------
#         like_price_count = 0
#         like_price_sum = 0
#         like_price2_sum = 0
#         like_distance_count = 0
#         like_distance_sum = 0
#         like_distance2_sum = 0
#         genre_list = []
#         like_genre_count = []

#         dislike_price_count = 0
#         dislike_price_sum = 0
#         dislike_price2_sum = 0
#         dislike_distance_count = 0
#         dislike_distance_sum = 0
#         dislike_distance2_sum = 0
#         dislike_genre_count = []

#         for r in pre_restaurants_info:
#             vote_like = r.votes_like
#             vote_dislike = r.votes_all - vote_like
#             if r.votes_all <= 0:
#                 continue

#             #price処理
#             price = r.price
#             if price is not None and price != 0:
#                 like_price_sum += vote_like * price
#                 like_price2_sum += vote_like * price*price
#                 like_price_count += vote_like
#                 dislike_price_sum += vote_dislike * price
#                 dislike_price2_sum += vote_dislike * price*price
#                 dislike_price_count += vote_dislike

#             #distance処理
#             distance = r["distance_float"]
#             like_distance_sum += vote_like * distance
#             like_distance2_sum += vote_like * distance*distance
#             like_distance_count += vote_like
#             dislike_distance_sum += vote_dislike * distance
#             dislike_distance2_sum += vote_dislike * distance*distance
#             dislike_distance_count += vote_dislike

#             #genre処理
#             genre = r["Genre"]
#             for g in genre:
#                 if g["Name"] not in genre_list:
#                     genre_list.append(g["Name"])
#                     like_genre_count.append(vote_like)
#                     dislike_genre_count.append(vote_dislike)
#                 else:
#                     like_genre_count[genre_list.index(g["Name"])] += vote_like
#                     dislike_genre_count[genre_list.index(g["Name"])] += vote_dislike

#         genre_feeling = {genre: {'Like':like,'Dislike':dislike} for genre, like, dislike in zip(genre_list, like_genre_count, dislike_genre_count)}
#         like_price_average = like_price_sum / like_price_count if like_price_count != 0 else 0
#         like_distance_average = like_distance_sum / like_distance_count if like_distance_count != 0 else 0
#         like_price_sigma = math.sqrt(like_price2_sum / like_price_count) if like_price_count != 0 else sys.float_info.max/16
#         like_distance_sigma = math.sqrt(like_distance2_sum / like_distance_count) if like_distance_count != 0 else sys.float_info.max/16
#         dislike_price_average = dislike_price_sum / dislike_price_count if dislike_price_count != 0 else 0
#         dislike_distance_average = dislike_distance_sum / dislike_distance_count if dislike_distance_count != 0 else 0
#         dislike_price_sigma = math.sqrt(dislike_price2_sum / dislike_price_count) if dislike_price_count != 0 else sys.float_info.max/16
#         dislike_distance_sigma = math.sqrt(dislike_distance2_sum / dislike_distance_count) if dislike_distance_count != 0 else sys.float_info.max/16
#         fetch_group.price_average = like_price_average
#         fetch_group.distance_average = like_distance_average
#         session.commit()

#         # recommend_priorityを計算する。 --------
#         weight_votes_like = 2.5
#         weight_price = 0.4
#         weight_distance = 0.3
#         weight_genre = 0.3
#         participants_count = database_functions.get_participants_count(group_id)
#         for ri in pre_restaurants_info:
#             fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==ri.id).one()
            
#             # votes_like_score
#             votes_like_score = participants_count * (fetch_vote.votes_all - fetch_vote.votes_like) - fetch_vote.votes_like # 1人でも反対した店は後回し
            
#             # price_score
#             price = ri.price
#             if price is not None and price != 0:
#                 price_score = (abs(price - like_price_average) / like_price_sigma - abs(price - dislike_price_average) / dislike_price_sigma) / 1000 # 偏差値のような何か
#             else:
#                 price_score = 1024 # 価格表示の無いものは後回しにしたいので，大きいスコアを与える
            
#             # distance_score
#             distance = ri.float
#             distance_score = abs(distance - like_distance_average) / like_distance_sigma - abs(distance - dislike_distance_average) / dislike_distance_sigma # 偏差値のような何か
            
#             # genre_score
#             genre_score = 0
#             for g in ri.genre:
#                 if g in genre_feeling:
#                     genre_score += genre_feeling[g]['Dislike'] - genre_feeling[g]['Like']
            
#             fetch_vote.recommend_priority = votes_like_score * weight_votes_like + price_score * weight_price + distance_score * weight_distance + genre_score * weight_genre
#             session.commit()


#     def search(self, fetch_group, group_id, user_id, histories_restaurants):
#         # YahooローカルサーチAPIで検索するクエリ
#         search_params = database_functions.get_search_params_from_fetch_group(fetch_group)

#         # 検索条件を追加
#         search_params.image = True  # 画像がある店
#         search_params.open_now = True  # 現在開店している店舗
#         search_params.set_start_and_results_from_stock(group_id, STOCK_COUNT, histories_restaurants)

#         # Yahooで検索
#         return call_api.search_restaurants_info(fetch_group, group_id,
#                                                      user_id, search_params)
 
#     def calc_priority(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):

#         pre_restaurants_info = restaurants_info_price_filter(fetch_group.max_price, fetch_group.min_price, pre_restaurants_info)

#         fetch_votes = session.query(Vote.votes_all).filter(Vote.group==group_id, Vote.votes_all>0).all()
#         if sum([v.votes_all for v in fetch_votes]) < 3:
#             pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)
#             return [r.id for r in pre_restaurants_info][0:RESPONSE_COUNT]
        
#         # Vote.recommend_priorityを計算する。
#         self.__calc_recommend_priority(fetch_group, group_id, pre_restaurants_info)
#         # t = threading.Thread(target=self.__calc_recommend_priority, args=(fetch_group, group_id, pre_restaurants_info))
#         # t.start()

#         # recommend_priorityの小さい順にユーザに送信する。
#         fetch_votes = session.query(Vote).filter(Vote.group==group_id, Vote.recommend_priority is not None).order_by(Vote.recommend_priority).all()
#         restaurants_ids = []
#         for fv in fetch_votes:
#             if fv.restaurant not in histories_restaurants:
#                 restaurants_ids.append(fv.restaurant)
#                 if len(restaurants_ids) == RESPONSE_COUNT:
#                     return restaurants_ids
#         return restaurants_ids


class RecommendSVM(Recommend):
    '''
    RecommendQueueの重みをSVMで決める

    1. 投票された結果はLIKE数の多い順に表示
    2. 未投票の結果は価格・距離・ジャンルからSVMで評価値を推定して表示
    '''

    def set_search_params(self,
                          fetch_group,
                          group_id,
                          user_id,
                          search_params,
                          histories_restaurants):

        # 検索条件を追加
        search_params.image = True  # 画像がある店
        search_params.open_now = True  # 現在開店している店舗
        search_params.set_start_and_results_from_stock(group_id, STOCK_COUNT, histories_restaurants)

        # Yahooの形式にして検索
        return search_params

    def __zero_recommend_priority(self, fetch_group, group_id, pre_restaurants_info):
        session = database_functions.get_db_session()
        for r_info in pre_restaurants_info:
            fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==r_info.id).one()
            fetch_vote.recommend_priority = 0
            session.commit()
        session.close()


    def __calc_recommend_priority(self, fetch_group, group_id, pre_restaurants_info):
        '''
        Vote.recommend_priorityを計算する。
        投票数が0だと死ぬ
        '''
        session = database_functions.get_db_session()

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
            if r.votes_all <= 0:
                continue
            voted_restaurants_count += 1
            vote_like = r.votes_like
            vote_dislike = r.votes_all - vote_like
            

            #price処理
            price = r.price
            if price is not None and price != 0:
                like_price_sum += vote_like * price
                like_price2_sum += vote_like * price*price
                like_price_count += vote_like
                dislike_price_sum += vote_dislike * price
                dislike_price2_sum += vote_dislike * price*price
                dislike_price_count += vote_dislike

            #distance処理
            distance = r.distance_float
            like_distance_sum += vote_like * distance
            like_distance2_sum += vote_like * distance*distance
            like_distance_count += vote_like
            dislike_distance_sum += vote_dislike * distance
            dislike_distance2_sum += vote_dislike * distance*distance
            dislike_distance_count += vote_dislike

            #genre処理
            genre = r.genre_name
            if genre is not None:
                for g in genre:
                    if g not in genre_list:
                        genre_list.append(g)
                        like_genre_count.append(vote_like)
                        dislike_genre_count.append(vote_dislike)
                    else:
                        like_genre_count[genre_list.index(g)] += vote_like
                        dislike_genre_count[genre_list.index(g)] += vote_dislike

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

        if like_price_sigma==0 or like_distance_sigma==0 or dislike_price_sigma==0 or dislike_distance_sigma==0:
            self.__zero_recommend_priority(self, fetch_group, group_id, pre_restaurants_info)
            session.close()
            return

        # recommend_priorityを計算する。--------

        participants_count = database_functions.get_participants_count(group_id) # 参加人数
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
            price = r.price
            if price is not None and price != 0:
                vec[0] = -abs(price - like_price_average) / like_price_sigma
                vec[1] = abs(price - dislike_price_average) / dislike_price_sigma
                vec[2] = -price / 1000
            else:
                vec[0] = 0
                vec[1] = 0
                if (like_price_count + dislike_price_count) == 0:
                    vec[2] = -(like_price_average + dislike_price_average) / 2
                else:
                    vec[2] = -(like_price_average * like_price_count + dislike_price_average * dislike_price_count) / (like_price_count + dislike_price_count)

            # distance_score
            distance = r.distance_float
            vec[3] = -abs(distance - like_distance_average) / like_distance_sigma * 1000
            vec[4] = abs(distance - dislike_distance_average) / dislike_distance_sigma * 1000
            
            # genre_score
            genre_score = 0
            if r.genre_name is not None:
                for g in r.genre_name:
                    if g in genre_feeling:
                        genre_score += genre_feeling[g]['Like'] - genre_feeling[g]['Dislike']
            vec[5] = genre_score * 1000

            vec[6] = r.yahoo_rating_float if r.yahoo_rating_float is not None else 0

            # 変数に格納
            if r.votes_all <= 0:
                rid_test[i_test] = r.id
                x_test[i_test][:] = vec[:]
                i_test += 1
            else:
                rid_train[i_train] = r.id
                x_train[i_train][:] = vec[:]
                y_train[i_train] = r.votes_like - participants_count * (r.votes_all - r.votes_like) # 訓練データのラベル
                i_train += 1

        print("i_train=", i_train, "i_test=", i_test)
        if i_test <= 0:
            print("i_test=", i_test, " , unvoted_restaurants_count=", unvoted_restaurants_count)
            for rid, y in zip(rid_train, y_train):
                fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==rid).one()
                fetch_vote.recommend_priority = y
                session.commit()
            session.close()
            return
        
        if i_train <= 0:
            print("i_train=", i_train, " , unvoted_restaurants_count=", unvoted_restaurants_count)
            for rid, y in zip(rid_train, y_train):
                fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==rid).one()
                fetch_vote.recommend_priority = 0
                session.commit()
            session.close()
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
        session.close()

    def __price_filter(self, group_id, max_price, min_price, restaurants_info):
        '''
        検索条件に合わない店は優先度を下げる
        TODO: 再度データベースのVoteを検索するので遅くなるかもしれない
        '''
        session = database_functions.get_db_session()
        if min_price is None:
            min_price = 0
        if max_price is None:
            for r_info in [r for r in restaurants_info if (r.price is not None and min_price > r.price)]:
                fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==r_info.id).one()
                fetch_vote.recommend_priority = -10000.0
                session.commit()
        else:
            for r_info in [r for r in restaurants_info if (r.price is None or min_price > r.price or r.price > max_price)]:
                fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==r_info.id).one()
                fetch_vote.recommend_priority = -10000.0
                session.commit()
        session.close()

    def calc_priority(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):

        session = database_functions.get_db_session()
        fetch_votes = session.query(Vote.votes_all).filter(Vote.group==group_id, Vote.votes_all>0).all()
        session.close()

        # Vote.recommend_priorityを計算する。
        if sum([v.votes_all for v in fetch_votes]) < 3:
            self.__zero_recommend_priority(fetch_group, group_id, pre_restaurants_info)
        else:
            self.__calc_recommend_priority(fetch_group, group_id, pre_restaurants_info)

        pre_restaurants_info = self.__price_filter(group_id, fetch_group.max_price, fetch_group.min_price, pre_restaurants_info)



    # def filter(self, fetch_group, group_id, user_id, pre_restaurants_info, histories_restaurants):

    #     pre_restaurants_info = restaurants_info_price_filter(fetch_group.max_price, fetch_group.min_price, pre_restaurants_info)

    #     fetch_votes = session.query(Vote.votes_all).filter(Vote.group==group_id, Vote.votes_all>0).all()
    #     if sum([v.votes_all for v in fetch_votes]) < 3:
    #         pre_restaurants_info = delete_duplicate_restaurants_info(group_id, user_id, pre_restaurants_info, histories_restaurants=histories_restaurants)
    #         return [r for r in pre_restaurants_info][0:RESPONSE_COUNT]
        
    #     # Vote.recommend_priorityを計算する。
    #     self.__calc_recommend_priority(fetch_group, group_id, pre_restaurants_info)
    #     # t = threading.Thread(target=self.__calc_recommend_priority, args=(fetch_group, group_id, pre_restaurants_info))
    #     # t.start()

    #     # recommend_priorityの小さい順にユーザに送信する。
    #     fetch_votes = session.query(Vote).filter(Vote.group==group_id, Vote.recommend_priority is not None).order_by(Vote.recommend_priority).all()
    #     restaurants_ids = []
    #     for fv in fetch_votes:
    #         if fv.restaurant not in histories_restaurants:
    #             restaurants_ids.append(fv.restaurant)
    #             if len(restaurants_ids) == RESPONSE_COUNT:
    #                 break

    #     restaurants_info = [r for r in pre_restaurants_info
    #                         if r.id in restaurants_ids]
    #     return restaurants_info




# ============================================================================================================
# recommend_mainで使う関数など

def filter_by_price(max_price, min_price, restaurants_info):
    '''
    検索条件に合わない店のpriorityを-1にする

    Parameters
    ----------------
    fetch_group
    restaurants_info

    Returns
    ----------------
    restaurnats_info
    '''
    if min_price is None:
        min_price = 0
    if max_price is None:
        return restaurants_info

    for i, _ in enumerate(restaurants_info):
        if restaurants_info[i].price is not None \
            and \
            (restaurants_info[i].price > max_price
             or restaurants_info[i].price < min_price):
            restaurants_info[i].recommend_priority = -1
    return restaurants_info

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
        histories_restaurants = database_functions.get_histories_restaurants(group_id, user_id)
    return [ri for ri in restaurants_info if not ri.id in histories_restaurants]



# ============================================================================================================
# recommend.pyで最初に呼ばれる

def recommend_main(fetch_group, group_id, user_id, first_time_flg=False):
    '''
    Yahoo local search APIで情報を検索し、json形式で情報を返す
    
    Parameters
    ----------------
    fetch_group : 
    group_id : int
    user_id : int
    
    Returns
    ----------------
    restaurant_ids : [dict]
        レスポンスするレストランidのリスト
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
    # TODO: search_paramを毎回更新して保存する
    recommend_method = config.MyConfig.RECOMMEND_METHOD
    if recommend_method == 'template':
        recomm = RecommendTemplate()
    elif recommend_method == 'simple':
        recomm = RecommendSimple()
    # elif recommend_method == 'yahoo':
    #     recomm = RecommendYahoo()
    # elif recommend_method == 'original':
    #     recomm = RecommendOriginal()
    # elif recommend_method == 'queue':
    #     recomm = RecommendQueue()
    elif recommend_method == 'svm':
        recomm = RecommendSVM()
    # elif recommend_method == 'local_search_test':
    #     return local_search_test(fetch_group, group_id, user_id)
    # elif recommend_method == 'local_search_test_URL':
    #     return local_search_test_URL(fetch_group, group_id, user_id)
    else:
        # error
        print("recommend_method is None.")
        recomm = RecommendSVM()

    # 初回は迅速に
    if first_time_flg:
        first_time_recommend_main(fetch_group, group_id, user_id, recomm)
        return []
    

    # 重複して表示しないようにするため、履歴を取得
    histories_restaurants = database_functions.get_histories_restaurants(group_id,
                                                                         user_id)
    
    # 結果が0件なら繰り返す
    for i in range(5):
        # 主な処理

        # 以前に検索したレストランのIDをデータベースから取得する(複数人で選ぶために)
        session = database_functions.get_db_session()
        restaurant_ids_from_db = session.query(Restaurant.id).filter(
            Vote.group == group_id,
            Vote.restaurant == Restaurant.id
            ).all()  # 未送信のもののみを取得するときはfilterに`Vote.votes_all==-1`を加える
        session.close()
        restaurant_ids_from_db = [r.id for r in restaurant_ids_from_db]
        restaurants_info_from_db = database_functions.load_restaurants_info(
            restaurant_ids_from_db,
            group_id)

        # グループの検索パラメータを読み込み
        params = database_functions.get_search_params_from_fetch_group(fetch_group)

        # 検索パラメータを設定
        params = recomm.set_search_params(fetch_group,
                                                    group_id,
                                                    user_id,
                                                    params,
                                                    histories_restaurants)
        # 検索条件を保存
        database_functions.set_search_params(group_id,
                                             params,
                                             fetch_group)

        # 検索
        restaurants_info = call_api.search_restaurants_info(fetch_group,
                                                            group_id,
                                                            user_id,
                                                            params)
        # 重複を省く
        restaurants_info = [r for r in restaurants_info if
                            r.id not in restaurant_ids_from_db]

        # 検索結果とDBを合わせる
        restaurants_info += restaurants_info_from_db

        database_functions.save_restaurants(restaurants_info)
        database_functions.save_votes(group_id, restaurants_info)

        if len(restaurants_info) >= 1:
            print(f"recommend_main: {recommend_method}\n"
                  f"  {len(restaurants_info_from_db)}/{len(restaurants_info)} items from DB\n"
                  f"  {len(restaurants_info) - len(restaurants_info_from_db)}/"
                  f"{len(restaurants_info)}items from API")

            print(f"recommend_main:"
                  f"results ={len(restaurants_info)}, "
                  f"history ={len(histories_restaurants)}")
            # searchでとってきた店のpriorityを計算し、
            recomm.calc_priority(fetch_group,
                                group_id,
                                user_id,
                                restaurants_info,
                                histories_restaurants)

            # お店の詳細を取得する
            restaurants_info = call_api.get_restaurants_info(fetch_group,
                                                     group_id,
                                                     restaurants_info)

            database_functions.save_restaurants(restaurants_info)
            database_functions.save_votes(group_id, restaurants_info)

            print(f"data_num {len(restaurants_info)}")
            return [r.id for r in restaurants_info if r is not None]

        else:
            # error: 検索結果なし
            print("検索結果なし:", i)
            # TODO: set_start_and_resultsからDB.Groupのstartをいじるのに変更
            database_functions.set_start()

            # if i >= 2 and recommend_method=="original":
            #     recomm = RecommendSimple()
            #     recommend_method = "simple"
            if i >= 3:
                histories_restaurants = [] # 結果が0件のときは履歴をなかったことにしてもう一周
    
    return []


def first_time_recommend_main(fetch_group, group_id, user_id, recomm:Recommend):
    # YahooローカルサーチAPIで検索するクエリ
    search_params = database_functions.get_search_params_from_fetch_group(fetch_group)

    # 検索条件を追加
    search_params.image = True  # 画像がある店
    search_params.sort = "hybrid"
    search_params.start = 0
    search_params.results = config.MyConfig.RESPONSE_COUNT * 2

    # Yahooの形式にして検索
    restaurants_info = call_api.search_restaurants_info(fetch_group,
                                                        group_id,
                                                        user_id,
                                                        search_params,
                                                        "yahoo_local_search")

    database_functions.save_restaurants(restaurants_info)
    database_functions.save_votes(group_id, restaurants_info)

    # searchでとってきた店のpriorityを計算
    recomm.calc_priority(fetch_group,
                        group_id,
                        user_id,
                        restaurants_info,
                        [])

    restaurants_info = call_api.get_restaurants_info(fetch_group,
                                                     group_id,
                                                     restaurants_info)

    database_functions.save_restaurants(restaurants_info)
    database_functions.save_votes(group_id, restaurants_info)

    return [r.id for r in restaurants_info if r is not None]