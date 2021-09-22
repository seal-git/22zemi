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
    search_params : dict
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
    elif api == "yahoo_local_search":
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
        api_f = api_functions.ApiFunctionsYahoo()
    elif api_method == "google":
        api_f = api_functions.piFunctionsGoogle()

        # データベースから店舗情報を取得
    print(f"get_restaurants_info: ids: {restaurant_ids}")

    restaurant_ids_del_none = [x for x in restaurant_ids if x is not None]
    restaurants_info = database_functions.load_stable_restaurants_info(
        restaurant_ids_del_none)

    # データベースにない店舗の情報をAPIで取得
    rest_ids = [rid for rid, r_info in zip(restaurant_ids, restaurants_info) if
                r_info is None]
    if len(rest_ids) > 0:
        rs_info = api_f.get_restaurants_info(fetch_group, group_id, rest_ids)
        for r_info in rs_info:
            restaurants_info[
                restaurant_ids_del_none.index(r_info['Restaurant_id'])] = r_info
    restaurants_info = [r for r in restaurants_info if
                        r is not None]  # feelingリクエストで架空のrestaurants_idだったときには、それを除く

    # 投票数と距離を計算
    restaurants_info = calc_info.add_votes_distance(fetch_group, group_id,
                                                    restaurants_info)
    # 画像生成
    restaurant_info["Image_references"] = calc_info.get_google_images(
        feature['Name']) if access_flag == "xxx" else []  # google
    # apiの画像のreferenceを保存
    restaurant_info["ImageFiles"] = calc_info.create_image(
        restaurant_info) if access_flag == "xxx" else []  # 1枚の画像のURLを保存
    if len(restaurant_info["Images"]) == 0:
        no_image_url = "http://drive.google.com/uc?export=view&id=1mUBPWv3kL-1u2K8LFe8p_tL3DoU65FJn"
        restaurant_info["Images"] = [no_image_url, no_image_url]

    return restaurants_info
