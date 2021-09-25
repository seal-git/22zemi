"""
call_api
search_restaurant_infoとget_restaurant_infoを実行する。


# 主な流れ
search_restaurants_info関数は検索条件(search_params)から店の情報(restaurants_info)を取得する。
get_restaurants_info関数はrestaurant_infoを更新する。

calc_info.pyには、APIと関係ないがget_restaurant_info内で呼ぶ関数があります。
"""

from app import api_functions, database_functions, calc_info
from app.database_setting import *
from app.internal_info import *


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

    if api == "google_nearby_search":
        # nearby searchで店舗情報を取得
        restaurants_info = api_functions.google_nearby_search(params)
    elif api == "google_text_search":
        # google_text_searchで店舗情報を取得
        restaurants_info = api_functions.google_text_search(params)
    elif api == "yahoo_local_search" or api == "yahoo":
        # yahoo_text_searchで店舗情報を取得
        restaurants_info = api_functions.yahoo_local_search(params)
    else:
        raise ValueError(f"api_function '{api}' does not exist")

    # データベースに店舗情報を保存
    database_functions.save_restaurants_info(restaurants_info)
    database_functions.save_votes(group_id, restaurants_info)

    # 以前に検索したレストランはデータベースから取得する(複数人で選ぶために)
    fetch_restaurants = session.query(Restaurant).filter(Vote.group == group_id,
                                                         Vote.restaurant == Restaurant.id
                                                         ).all()  # 未送信のもののみを取得するときはfilterに`Vote.votes_all==-1`を加える
    restaurants_info_from_db = [
        database_functions.get_restaurant_info_from_db(r) for r in
        fetch_restaurants]
    restaurants_list_from_db = [r.id for r in restaurants_info_from_db]
    restaurants_info = restaurants_info_from_db + [r for r in restaurants_info if r.id not in restaurants_list_from_db]

    # 投票数と距離を計算
    restaurants_info = calc_info.add_votes_distance(fetch_group, group_id,
                                                    restaurants_info)
    # レコメンドスコアを計算
    restaurants_info = calc_info.calc_recommend_score(fetch_group, restaurants_info)

    ## 設定された時間でのpriceを設定する
    restaurants_info = calc_info.add_price(fetch_group,
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

    # データベースから店舗情報を取得(full_info_flagが必要？)
    restaurant_ids_del_none = [r.id for r in restaurants_info if r.id is not None]
    restaurants_info = database_functions.load_stable_restaurants_info(restaurant_ids_del_none,
                                                                       group_id)

    # データベースにない情報を店舗ごとにAPIで取得
    ## feelingリクエストで架空のrestaurants_idだったときには、それを除く
    restaurants_info = [r for r in restaurants_info if
                        r is not None]
    for i in range(len(restaurants_info)):
        if restaurants_info[i].yahoo_id is not None and restaurants_info[i].google_id is not None:
            # APIから取得済みの場合は飛ばす
            continue
        if restaurants_info[i].yahoo_id is None:
            ## yahoo_idを追加
            restaurants_info[i] = api_functions.yahoo_local_search(r_info=restaurants_info[i])[0]
        if restaurants_info[i].google_id is None:
            ## google_idを追加
            # restaurants_info[i] = api_functions.google_find_place(r_info=restaurants_info[i])
            pass
        if restaurants_info[i].yahoo_id is not None:
            ## yahooレビューを取得
            restaurants_info[i] = api_functions.yahoo_review(restaurants_info[i])

        if restaurants_info[i].google_id is not None:
            ## googleの情報を追加
            # restaurants_info[i] = api_functions.google_place_details(r_info=restaurants_info[i])
            pass

    # Googleから画像を取得する
    if config.MyConfig.GET_GOOGLE_IMAGE:
        restaurants_info = calc_info.get_google_images_list(restaurants_info)
    ## 画像生成
    # restaurants_info = calc_info.add_google_images(restaurants_info)


    # グループごとの情報を計算する

    ## レーティングの文字列を生成する
    restaurants_info = calc_info.add_review_rating(restaurants_info)

    database_functions.save_restaurants_info(restaurants_info)
    database_functions.save_votes(group_id, restaurants_info)

    return restaurants_info


