"""
call_api
search_restaurant_infoとget_restaurant_infoを実行する。
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

    # 以前に検索したレストランはデータベースから取得する
    fetch_restaurants = session.query(Restaurant).filter(Vote.group == group_id,
                                                         Vote.restaurant == Restaurant.id).all()  # 未送信のもののみを取得するときはfilterに`Vote.votes_all==-1`を加える
    restaurants_info_from_db = [
        database_functions.get_restaurant_info_from_fetch_restaurant(r) for r in
        fetch_restaurants]
    restaurants_list_from_db = [r.id for r in restaurants_info_from_db]
    restaurants_info = restaurants_info_from_db + [r for r in restaurants_info if r.id not in restaurants_list_from_db]

    # 投票数と距離を計算
    restaurants_info = calc_info.add_votes_distance(fetch_group, group_id,
                                                    restaurants_info)
    # レコメンドスコアを計算
    restaurants_info = calc_info.calc_recommend_score(fetch_group, group_id, restaurants_info)

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
    # restaurant_ids_del_none = [x for x in restaurant_ids if x is not None]
    # restaurants_info = database_functions.load_stable_restaurants_info(
    #     restaurant_ids_del_none)

    # データベースにない情報を店舗ごとにAPIで取得
    # feelingリクエストで架空のrestaurants_idだったときには、それを除く
    restaurants_info = [r for r in restaurants_info if
                        r is not None]
    for i in range(len(restaurants_info)):
        if restaurants_info[i].yahoo_id is None:
            # yahooの情報を追加
            restaurants_info[i] = api_functions.yahoo_local_search(r_info=restaurants_info[i])[0]
        if restaurants_info[i].google_id is None:
            # TODO: googleの情報を追加
            pass
            # restaurants_info[i] = api_functions.google_find_place(r_info=restaurants_info[i])[0]

    # 投票数と距離を計算
    restaurants_info = calc_info.add_votes_distance(fetch_group, group_id,
                                                    restaurants_info)
    # 画像生成
    # restaurant_info["Image_references"] = calc_info.get_google_images(
    #     feature['Name']) if access_flag == "xxx" else []  # google
    # # apiの画像のreferenceを保存
    # restaurant_info["ImageFiles"] = calc_info.create_image(
    #     restaurant_info) if access_flag == "xxx" else []  # 1枚の画像のURLを保存
    # if len(restaurant_info["Images"]) == 0:
    #     no_image_url = "http://drive.google.com/uc?export=view&id=1mUBPWv3kL-1u2K8LFe8p_tL3DoU65FJn"
    #     restaurant_info["Images"] = [no_image_url, no_image_url]

    # 設定された時間でのpriceを設定する
    restaurants_info = calc_info.add_price(fetch_group,
                                           group_id,
                                           restaurants_info)

    return restaurants_info


def get_restaurants_info_from_recommend_priority(fetch_group, group_id,
                                                 user_id):
    '''
    call_api行き
    あらかじめ優先度が計算されていたら、優先度順にレストランを取得する。

    Parameters
    ----------------
    fetch_group
    group_id
    user_id

    Returns
    ----------------
    restaurnts_info : [dict]
    '''
    histories_restaurants = database_functions.get_histories_restaurants(
        group_id, user_id)
    fetch_votes = session.query(Vote).filter(Vote.group == group_id,
                                             Vote.recommend_priority is not None).order_by(
        Vote.recommend_priority).all()
    restaurants_ids = []
    for fv in fetch_votes:
        if fv.restaurant not in histories_restaurants:
            restaurants_ids.append(fv.restaurant)
            if len(restaurants_ids) == config.MyConfig.RESPONSE_COUNT:
                return get_restaurants_info(fetch_group,
                                            group_id,
                                            restaurants_ids)

    # まだ優先度を計算していない時や，RecommendSimple等で優先度を計算しない時
    fetch_votes = session.query(Vote).filter(Vote.group == group_id,
                                             Vote.recommend_priority is None).all()
    for fv in fetch_votes:
        if fv.restaurant not in histories_restaurants:
            restaurants_ids.append(fv.restaurant)
            if len(restaurants_ids) == config.MyConfig.RESPONSE_COUNT:
                return get_restaurants_info(fetch_group,
                                            group_id,
                                            restaurants_ids)

    # ストックしている店舗数が足りない時。最初のリクエスト等。
    return []