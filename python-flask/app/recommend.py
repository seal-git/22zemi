from app import api_functions
import json

RESULTS_COUNT = 3 # 一回に返す店舗の数

def recommend_simple(current_group, group_id, user_id):
    '''
    レコメンドは Yahoo Local Search に任せる
    '''
    
    coordinates = current_group[group_id]['Coordinates']
    address = current_group[group_id]['Address']
    request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    
     # YahooローカルサーチAPIで検索するクエリ
    local_search_params = {
        # 中心地から1km以内のグルメを検索
        'lat': coordinates[0], # 緯度
        'lon': coordinates[1], # 経度
        'dist': 3, # 中心地点からの距離 # 最大20km
        'gc': '01', # グルメ
        'image': True, # 画像がある店
        'open': 'now', # 現在開店している店舗
        'sort': 'hybrid', # 評価や距離などを総合してソート
        'start': RESULTS_COUNT * request_count, # 表示範囲：開始位置
        'results': RESULTS_COUNT # 表示範囲：店舗数
    }

    # Yahoo local search APIで店舗情報を取得
    local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(coordinates, address, local_search_params)
    return json.dumps(result_json, ensure_ascii=False)


def recommend_industry_code(current_group, group_id, user_id):
    # TODO: 業種コードによるレコメンド
    return [], []

def recommend_review(current_group, group_id, user_id):
    # TODO: 口コミによるレコメンド
    return [], []


def recommend_template(current_group, group_id, user_id):
    '''
    simpleと同じ動きをするテンプレート
    '''
    LOCAL_SEARCH_RESULTS_COUNT = 30 # 一回に取得する店舗の数 # RESULTS_COUNTの倍数
    
    coordinates = current_group[group_id]['Coordinates']
    address = current_group[group_id]['Address']
    request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    
     # TODO: YahooローカルサーチAPIで検索するクエリ
    local_search_params = {
        # 中心地から1km以内のグルメを検索
        'lat': coordinates[0], # 緯度
        'lon': coordinates[1], # 経度
        'dist': 3, # 中心地点からの距離 # 最大20km
        'gc': '01', # グルメ
        'image': True, # 画像がある店
        'open': 'now', # 現在開店している店舗
        'sort': 'hybrid', # 評価や距離などを総合してソート
        'start': LOCAL_SEARCH_RESULTS_COUNT * int(request_count * RESULTS_COUNT / LOCAL_SEARCH_RESULTS_COUNT), # 表示範囲：開始位置
        'results': LOCAL_SEARCH_RESULTS_COUNT # 表示範囲：店舗数
    }

    # Yahoo local search APIで店舗情報を取得
    local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(coordinates, address, local_search_params)
    
    # TODO: 重みを計算
    weight = [0] * LOCAL_SEARCH_RESULTS_COUNT
    for i,local_search_feature in enumerate(local_search_json):
        weight[i] = LOCAL_SEARCH_RESULTS_COUNT - i

    # 重み順にソートして出力
    result_json = sorted(zip(weight, result_json), key=lambda x:x[0], reverse=True)
    result_json = [rj[1] for rj in result_json]
    result_json = result_json[request_count * RESULTS_COUNT : (request_count+1) * RESULTS_COUNT]
    return json.dumps(result_json, ensure_ascii=False)


def local_search_test(current_group, group_id, user_id):
    '''
    Yahoo Local Searchの出力を見る
    '''
    coordinates = current_group[group_id]['Coordinates']
    address = current_group[group_id]['Address']
    request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    
     # YahooローカルサーチAPIで検索するクエリ
    local_search_params = {
        # 中心地から1km以内のグルメを検索
        'lat': coordinates[0], # 緯度
        'lon': coordinates[1], # 経度
        'dist': 3, # 中心地点からの距離 # 最大20km
        'gc': '01', # グルメ
        'image': True, # 画像がある店
        'open': 'now', # 現在開店している店舗
        'sort': 'hybrid', # 評価や距離などを総合してソート
        'start': RESULTS_COUNT * request_count, # 表示範囲：開始位置
        'results': RESULTS_COUNT # 表示範囲：店舗数
    }

    # Yahoo local search APIで店舗情報を取得
    local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(coordinates, address, local_search_params)
    return str(local_search_json)


def recommend_main(current_group, group_id, user_id, recommend_method):
    '''
    Yahoo local search APIで情報を検索し、json形式で情報を返す
    
    Parameters
    ----------------
    current_group : dictionary
    group_id : string
    user_id : string
    recommend_method ; string
    
    Returns
    ----------------
    restaurant_info : string
        レスポンスするレストラン情報をjson形式で返す。
    '''
    
    # TODO: レコメンド関数の追加
    if recommend_method == 'simple':
        result_json = recommend_simple(current_group, group_id, user_id)
    elif recommend_method == 'template':
        result_json = recommend_template(current_group, group_id, user_id)
    elif recommend_method == 'industry_code':
        result_json = recommend_industry_code(current_group, group_id, user_id)
    elif recommend_method == 'review':
        result_json = recommend_review(current_group, group_id, user_id)
    elif recommend_method == 'local_search_test':
        result_json = local_search_test(current_group, group_id, user_id)
    else:
        result_json = recommend_simple(current_group, group_id, user_id)

    return result_json

