from app import api_functions
import json
import os

RESULTS_COUNT = 3 # 一回に返す店舗の数


def recommend_simple(current_group, group_id, user_id, recommend_method):
    '''
    レコメンドは Yahoo Local Search に任せる
    '''
    
    coordinates = current_group[group_id]['Coordinates']
    request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    
    # YahooローカルサーチAPIで検索するクエリ
    local_search_params = {
        # 中心地から1km以内のグルメを検索
        'lat': coordinates[0], # 緯度
        'lon': coordinates[1], # 経度
        'dist': 3, # 中心地点からの距離 # 最大20km
        'gc': '01', # グルメ
        'image': True, # 画像がある店
        # 'open': 'now', # 現在開店している店舗 # TODO
        'sort': recommend_method, # hyblid # 評価や距離などを総合してソート
        'start': RESULTS_COUNT * request_count, # 表示範囲：開始位置
        'results': RESULTS_COUNT # 表示範囲：店舗数
    }
    local_search_params.update(current_group[group_id]['FilterParams'])

    # Yahoo local search APIで店舗情報を取得
    local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(current_group[group_id], local_search_params)
    return json.dumps(result_json, ensure_ascii=False)


def recommend_industry(current_group, group_id, user_id):
    '''
    業種コードによるレコメンド
    '''
    # TODO: 業種コードによるレコメンド
    return '[]'

def recommend_review_words(current_group, group_id, user_id):
    '''
    口コミによるレコメンド
    ReviewRatingが3以上の店舗を返す
    一回のレスポンスで返す店舗数は0~10の間
    '''
    # TODO: 口コミによるレコメンド
    LOCAL_SEARCH_RESULTS_COUNT = 10 # 一回に取得する店舗の数
    coordinates = current_group[group_id]['Coordinates']
    address = current_group[group_id]['Address']
    
    for i in range(1000000):
        request_count = current_group[group_id]['Users'][user_id]['RequestCount']

        local_search_params = {
            # 中心地から1km以内のグルメを検索
            'lat': coordinates[0], # 緯度
            'lon': coordinates[1], # 経度
            'dist': 3, # 中心地点からの距離 # 最大20km
            'gc': '01', # グルメ
            'image': True, # 画像がある店
            'open': 'now', # 現在開店している店舗
            'sort': 'hybrid', # 評価や距離などを総合してソート
            'start': LOCAL_SEARCH_RESULTS_COUNT * request_count, # 表示範囲：開始位置
            'results': LOCAL_SEARCH_RESULTS_COUNT
        }
        local_search_params.update(current_group[group_id]['FilterParams'])
    
        local_search_json, result_json = api_functions.get_restaurant_info_from_local_search_params(coordinates, address, local_search_params)
        result_json = sorted(result_json, key=lambda x:x['ReviewRating'], reverse=True)
        stop_index = [i for i, x in enumerate(result_json) if x['ReviewRating'] < 3][0]
        result_json = result_json[:stop_index]
        if len(result_json) >= 1:
            return json.dumps(result_json, ensure_ascii=False)
        current_group[group_id]['Users'][user_id]['RequestCount'] += 1


def recommend_template(current_group, group_id, user_id):
    '''
    simpleと同じ動きをするテンプレート
    '''
    LOCAL_SEARCH_RESULTS_COUNT = 30 # 一回に取得する店舗の数 # RESULTS_COUNTの倍数
    
    coordinates = current_group[group_id]['Coordinates']
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
    local_search_params.update(current_group[group_id]['FilterParams'])

    # Yahoo local search APIで店舗情報を取得
    local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(current_group[group_id], local_search_params)
    
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
    simpleのYahoo Local Searchの出力を見る
    '''
    coordinates = current_group[group_id]['Coordinates']
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
    local_search_params.update(current_group[group_id]['FilterParams'])

    # Yahoo local search APIで店舗情報を取得
    local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(current_group[group_id], local_search_params)
    return str(local_search_json)

def local_search_test_URL(current_group, group_id, user_id):
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
        'dist': 3, # 中心地点からの距離 # 最大20km
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
    # ratingは、星の数順にソートします。
    # scoreは、スコア順にソートします。
    # hybridは、口コミ件数や星の数などを重み付けした値の順にソートします。
    # reviewは、口コミ件数にソートします。
    # kanaは、アイウエオ順にソートします。
    # priceは、金額順にソートします。
    # distは、2点間の直線距離順にソートします。（geoより高速です）
    # geoは、球面三角法による2点間の距離順にソートします。
    
    # TODO: レコメンド関数の追加
    if recommend_method in ['rating', 'score', 'hyblid', 'review', 'kana', 'price', 'dist', 'geo', '-rating', '-score', '-hyblid', '-review', '-kana', '-price', '-dist', '-geo']:
        result_json = recommend_simple(current_group, group_id, user_id, recommend_method)
    elif recommend_method == 'template':
        result_json = recommend_template(current_group, group_id, user_id)
    elif recommend_method == 'industry':
        result_json = recommend_industry(current_group, group_id, user_id)
    elif recommend_method == 'review_words':
        result_json = recommend_review_words(current_group, group_id, user_id)
    elif recommend_method == 'local_search_test':
        result_json = local_search_test(current_group, group_id, user_id)
    elif recommend_method == 'local_search_test_URL':
        result_json = local_search_test_URL(current_group, group_id, user_id)
    else:
        result_json = recommend_simple(current_group, group_id, user_id, 'hyblid')

    return result_json

