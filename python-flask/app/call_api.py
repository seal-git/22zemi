"""
call_api
search_restaurant_infoとget_restaurant_infoを実行する。


# 主な流れ
search_restaurants_info関数は検索条件(search_params)から店の情報(restaurants_info)を取得する。
get_restaurants_info関数はrestaurant_infoを更新する。

calc_info.pyには、APIと関係ないがget_restaurant_info内で呼ぶ関数があります。
"""

from app import api_functions, database_functions, calc_info, api_functions_for_test
from app.database_setting import *
from app.internal_info import *
import threading

# ============================================================================================================


def search_restaurants_info(fetch_group,
                            group_id,
                            user_id,
                            params: Params,
                            api="yahoo_local_search"):
    '''
    レコメンドするために条件に合う店を取ってくる
    recommend.pyのRecommend.search()から呼ばれる。
    api指定が不正ならyahoo_local_searchで検索

    Parameters
    ----------------
    fetch_group :
        データベースのグループ情報
    group_id : int
    user_id : int
    search_params : Params
        検索条件

    Returns
    ----------------
    restaurants_info : [dict]
        レスポンスするレストラン情報を返す。
    '''

    api = 'hotpepper_search'

    # レストランを検索する
    if api == "google_nearby_search":
        # nearby searchで店舗情報を取得
        restaurants_info = api_functions.google_nearby_search(params)
    elif api == "google_text_search":
        # google_text_searchで店舗情報を取得
        restaurants_info = api_functions.google_text_search(params)
    elif api == "yahoo_local_search" or api == "yahoo":
        # yahoo_text_searchで店舗情報を取得
        restaurants_info = api_functions.yahoo_local_search(params)
    elif api== "hotpepper_search" or api == 'hotpepper':
        restaurants_info = api_functions.hotpepper_search(params)
    else:
        raise ValueError(f"api_function '{api}' does not exist")


    # グループごとの情報を計算
    ## 距離を計算
    restaurants_info = calc_info.add_distance(fetch_group,
                                                    group_id,
                                                    restaurants_info)
    ## 設定された日付のopen_hourを設定する
    restaurants_info = calc_info.add_open_hour(fetch_group,
                                           restaurants_info)
    ## 設定された時間でのpriceを設定する
    restaurants_info = calc_info.add_price(fetch_group,
                                           restaurants_info)
    ## レコメンドスコアを計算
    restaurants_info = calc_info.calc_recommend_score(fetch_group,
                                                      restaurants_info)

    return restaurants_info


def get_restaurants_info(fetch_group,
                         group_id,
                         restaurants_info: [RestaurantInfo]):
    '''
    restaurants_infoの情報を追加してユーザに返す
    recommend.pyのRecommend.response_info()から呼ばれる。listリクエストでも呼ばれる。
    restaurants_idsの順序でrestaurants_infoを返す。

    Parameters
    ----------------
    fetch_group :
        データベースのグループ情報
    group_id: int
        グループID
    restaurants_info : [string]
        restaurant_idのリスト

    Returns
    ----------------
    restaurants_info : [dict]
        レスポンスするレストラン情報を返す。
    '''

    print(f"get_restaurants_info: {len(restaurants_info)} items")


    # 未取得の情報を店舗ごとにAPIで取得
    new_restaurants_info = [None for r in restaurants_info]
    thread_list = [None for r in restaurants_info]
    for i , r_info in enumerate(restaurants_info): # 並列で情報取得
        thread_list[i] = threading.Thread(target=thread_get_restaurant_info,
                                          args=(i, r_info, new_restaurants_info))
        thread_list[i].start()
    for t in thread_list:
        t.join()

    restaurants_info = new_restaurants_info

    # グループごとの情報を計算する

    ## 画像生成
    # restaurants_info = calc_info.add_google_images(restaurants_info)

    ## レーティングの文字列を生成する
    ## 投票数を計算
    restaurants_info = calc_info.add_votes(fetch_group,
                                                    group_id,
                                                    restaurants_info)

    restaurants_info = calc_info.add_review_rating(restaurants_info)

    return restaurants_info


def thread_get_restaurant_info(i, r_info, new_restaurants_info):
    if r_info.yahoo_id is not None and r_info.google_id is not None:
        # APIから取得済みの場合は飛ばす
        new_restaurants_info[i] = r_info
        return
    if r_info.yahoo_id is None:
        ## yahoo_idを追加
        r_info = api_functions.yahoo_local_search(r_info=r_info)[0]
    if r_info.google_id is None:
        ## google_idを追加
        if config.MyConfig.GET_GOOGLE_IMAGE:
            r_info = api_functions.google_find_place(r_info=r_info)
        else:
            r_info = api_functions_for_test.google_find_place(r_info=r_info)


    if r_info.yahoo_id is not None:
        ## yahooレビューを取得
        r_info = api_functions.yahoo_review(r_info)

    if r_info.google_id is not None:
        ## googleの情報を追加
        if config.MyConfig.USE_GOOGLE_API:
            r_info = api_functions.google_place_details(r_info=r_info)
        else:
            r_info = api_functions_for_test.google_place_details(r_info=r_info)

    if config.MyConfig.GET_GOOGLE_IMAGE:
        r_info = calc_info.get_google_images(r_info)

    new_restaurants_info[i] = r_info
    print(f"thread{i}: {r_info.name}, {r_info.google_id}")
    return



