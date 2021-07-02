from app import api_functions
import json
import os
import random

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

def save_result(current_group, group_id, user_id, result_json, params = {}):
    for i in range(len(result_json)):
        if result_json[i]["Restaurant_id"] not in current_group[group_id]['Restaurants']:
             current_group[group_id]["Restaurants"][result_json[i]["Restaurant_id"]] = {"info":result_json[i]}
             current_group[group_id]['Restaurants'][result_json[i]["Restaurant_id"]]['Like'] = set()
             current_group[group_id]['Restaurants'][result_json[i]["Restaurant_id"]]['All'] = set()

    if "dist" in params.keys():
        dist = params["dist"]
        current_group[group_id]["GroupDistance"] = dist
    # else:
    #     current_group[group_id]["GroupDistance"] = None
    if "price" in params.keys():
        price = params["price"]
        current_group[group_id]["GroupPrice"] = price
    # else:
    #     current_group[group_id]["GroupPrice"] = None


def delete_duplicate_result(current_group, group_id, user_id, result_json):
    result_json_tmp = []
    for i in range(len(result_json)):
        if result_json[i]["Restaurant_id"] not in current_group[group_id]["Restaurants"]:
            result_json_tmp.append(result_json[i])
    return result_json_tmp

def recommend_simple(current_group, group_id, user_id, recommend_method, params={}):
    '''
    レコメンドは Yahoo Local Search に任せる
    '''
    
    coordinates = current_group[group_id]['Coordinates']
    request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    code = '0' + random.choice(list(category_code.values()))
    if "dist" in params.keys():
        dist = params["dist"]
    else:
        dist = MAX_DISTANCE
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
        'gc': '01', # グルメ
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
            'dist': MAX_DISTANCE, # 中心地点からの距離 # 最大20km
            'gc': '01', # グルメ
            'image': 'true', # 画像がある店
            'open': 'now', # 現在開店している店舗
            'sort': 'hybrid', # 評価や距離などを総合してソート
            'start': LOCAL_SEARCH_RESULTS_COUNT * request_count, # 表示範囲：開始位置
            'results': LOCAL_SEARCH_RESULTS_COUNT
        }
        local_search_params.update(current_group[group_id]['FilterParams'])
    
        local_search_json, result_json = api_functions.get_restaurant_info_from_local_search_params(coordinates, address, local_search_params)
        save_result(current_group, group_id, user_id, result_json)
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
    LOCAL_SEARCH_RESULTS_COUNT = RESULTS_COUNT*3 # 一回に取得する店舗の数 # RESULTS_COUNTの倍数
    
    coordinates = current_group[group_id]['Coordinates']
    request_count = current_group[group_id]['Users'][user_id]['RequestCount']
    
     # TODO: YahooローカルサーチAPIで検索するクエリ
    local_search_params = {
        # 中心地から1km以内のグルメを検索
        'lat': coordinates[0], # 緯度
        'lon': coordinates[1], # 経度
        'dist': MAX_DISTANCE, # 中心地点からの距離 # 最大20km
        'gc': '01', # グルメ
        'image': 'true', # 画像がある店
        'open': 'now', # 現在開店している店舗
        'sort': 'hybrid', # 評価や距離などを総合してソート
        'start': LOCAL_SEARCH_RESULTS_COUNT * int(request_count * RESULTS_COUNT / LOCAL_SEARCH_RESULTS_COUNT), # 表示範囲：開始位置
        'results': LOCAL_SEARCH_RESULTS_COUNT # 表示範囲：店舗数
    }
    local_search_params.update(current_group[group_id]['FilterParams'])

    # Yahoo local search APIで店舗情報を取得
    local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(current_group[group_id], local_search_params)
    save_result(current_group, group_id, user_id, result_json)
    # TODO: 重みを計算
    weight = [0] * LOCAL_SEARCH_RESULTS_COUNT
    for i,local_search_feature in enumerate(local_search_json):
        weight[i] = LOCAL_SEARCH_RESULTS_COUNT - i

    # 重み順にソートして出力
    result_json = sorted(zip(weight, result_json), key=lambda x:x[0], reverse=True)
    result_json = [rj[1] for rj in result_json]
    result_json = result_json[request_count * RESULTS_COUNT : (request_count+1) * RESULTS_COUNT]
    return result_json

def recommend_genre(current_group, group_id, user_id):
    
    simple_method = random.choice(['rating', 'score', 'hyblid', 'review', 'kana', 'price', 'dist', 'geo', '-rating', '-score', '-hyblid', '-review', '-kana', '-price', '-dist', '-geo'])
    #データがなければsimple
    if len(current_group[group_id]["Restaurants"].keys()) == 0:
        print("start")
        result_json = recommend_simple(current_group, group_id, user_id, simple_method)
        return result_json

    else:
        LOCAL_SEARCH_RESULTS_COUNT = 10 # 一回に取得する店舗の数 # RESULTS_COUNTの倍数
        coordinates = current_group[group_id]['Coordinates']
        request_count = current_group[group_id]['Users'][user_id]['RequestCount']
        group_result = current_group[group_id]["Restaurants"]
        restaurant_ids = list(group_result.keys())
        keep_restaurant_ids = []
        through_restaurant_ids = []
        keep_list = [] #[[Like数, 価格, 距離, ジャンル名, ジャンルコード ], ...]
        through_list = [] #[[All数, Like数, 価格, 距離,　ジャンル名, ジャンルコード], ...]
        for r_id in restaurant_ids:
            if len(group_result[r_id]["Like"]) > 0:
                keep_restaurant_ids.append(r_id)
                keep_list.append([ len(group_result[r_id]['Like']), group_result[r_id]['info']['Price'], \
                    group_result[r_id]['info']['distance_float'], group_result[r_id]['info']['Genre'][0]['Name'], \
                    group_result[r_id]['info']['Genre'][0]['Code'] ] )
            else:
                through_restaurant_ids.append(r_id)
                through_list.append([ len(group_result[r_id]['All']), len(group_result[r_id]['Like']), group_result[r_id]['info']['Price'], \
                    group_result[r_id]['info']['distance_float'], group_result[r_id]['info']['Genre'][0]['Name'], \
                        group_result[r_id]['info']['Genre'][0]['Code'] ] )
        
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
            result_json = recommend_simple(current_group, group_id, user_id, simple_method)
            return result_json

        #ジャンル keep数 or through数が多い順にジャンルをみる
        if recommend_type == "keep":
            genre = [l[3] for l in keep_list]
        elif recommend_type == "through":
            genre = [l[4] for l in through_list]
        genre_count = [] #[[カウント数, ジャンル名], ...]
        counted = []
        for c in genre:
            if c not in counted:
                genre_count.append([genre.count(c), c])
                counted.append(c)
        genre_count.sort(reverse=True)
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
            result_json = recommend_simple(current_group, group_id, user_id, simple_method, params)
            return json.dumps(result_json, ensure_ascii=False)

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
    
    local_search_json, result_json =  api_functions.get_restaurant_info_from_local_search_params(current_group[group_id], local_search_params)
    result_json = delete_duplicate_result(current_group, group_id, user_id, result_json)
    result_json = get_result_json_price_filter(meanprice, result_json)

    if len(result_json) == 0:
        print("No Data: recommend genre restaurant")
        result_json = recommend_simple(current_group, group_id, user_id, simple_method, params)
        return result_json
    
    print("recommend_genre")
    print(f"data_num {len(result_json)}")
    save_result(current_group, group_id, user_id, result_json, params) #レコメンドの結果を保存
    return result_json

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
    elif recommend_method == 'genre':
        result_json = recommend_genre(current_group, group_id, user_id)
    else:
        result_json = recommend_simple(current_group, group_id, user_id, 'hyblid')
        # result_json = recommend_genre(current_group, group_id, user_id)

    return json.dumps(result_json, ensure_ascii=False)


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