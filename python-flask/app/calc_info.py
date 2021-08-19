import math

def distance_display(distance):
    '''
    距離の表示を整形します
    '''
    distance = int(distance)
    if len(str(distance)) > 3:
        distance = round(distance / 1000, 1)
        return str(distance) + "km"
    return str(distance) + "m"

    
def calc_recommend_score(fetch_group, group_id, result_json):
    '''
    オススメ度を計算する
    
     Parameters
    ----------------
    result_json : dict
    
    Returns
    ----------------
    result_json : dict
        追加
        resul_json[i]["RecommendScore"] : float
            オススメ度をパーセントで返す
    '''
    
    # オススメ度を計算
    # 価格帯, 距離, 投票数を元に計算 
    # キープされたお店の中で、共通している条件が多いほど高スコア
    # 以下はrestaurant_idを格納
    
    try:
        group_price = fetch_group.group_price #グループの平均価格
        group_distance = fetch_group.group_distance * 1000 #グループの平均距離 m
    except:
        group_price = None
        group_distance = None
    score_list = []
    index_list = []
    for i in range(len(result_json)):
        try:
            price = int(result_json[i]["Price"])
            distance = result_json[i]["distance_float"]
            try:
                price_score = 1 if price <= group_price else group_price / price #グループ価格に対する比でスコア付
            except:
                price_score = 0

            try:
                distance_score = 1 if distance <= group_distance else group_distance / distance #グループ距離に対する比でスコア付
            except:
                distance_score = 0

            #投票されていればスコアが計算される
            if result_json[i]["VotesAll"] > 0:
                vote_score = (result_json[i]["VotesLike"] / result_json[i]["VotesAll"])
                score = int(round(((price_score + distance_score + vote_score) / 3) * 100, 0))
                #result_json[i]["RecommendScore"] = score
                score_list.append(score)
                index_list.append(i)
            else:
                score = 0
                score_list.append(score)
                index_list.append(i)
        except:
            score_list.append(0)
            index_list.append(i)

    #normalize score
    max_score = max(score_list)
    min_score = min(score_list)
    norm_score_list = []
    M = 100 #設定したい最大値
    m = 50 #設定したい最小値
    for s in score_list:
        try:
            norm_score = ((s - min_score)*(M - m) / (max_score - min_score)) + m
        except:
            norm_score = 100 #maxとminが同じ場合は全て100
        norm_score_list.append(norm_score)
    
    for i, n_s in zip(index_list, norm_score_list):
        result_json[i]["RecommendScore"] = round(n_s)

    return result_json
